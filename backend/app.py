import os
from flask import Flask, jsonify, request
from flask_migrate import Migrate
from sqlalchemy import Date, Text, DateTime
from dateutil import parser
from trends_service import get_rising_queries, get_trending_searches, get_interest_over_time, get_historical_interest
import semrush_service
import recommendation_service
import wordpress_service
import forecasting_service
import shopify_service
import pricing_engine
from models import db, TrackedKeyword, KeywordRank, BlogPost, PlatformIntegration, Product, PricingRule

# App setup
app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))

# Database setup
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'app.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
migrate = Migrate(app, db)

# --- API Routes ---

@app.route('/')
def hello_world():
    return 'Hello, World!'

@app.route('/api/content-ideas')
def content_ideas():
    topic = request.args.get('topic')
    if not topic:
        return jsonify({"error": "A 'topic' query parameter is required."}), 400

    timeframe = request.args.get('timeframe', 'today 3-m')
    geo = request.args.get('geo', '')
    cat = request.args.get('cat', 0, type=int)
    gprop = request.args.get('gprop', '')

    ideas = get_rising_queries(
        keyword=topic,
        timeframe=timeframe,
        geo=geo,
        cat=cat,
        gprop=gprop
    )
    return jsonify(ideas)

@app.route('/api/trending-topics')
def trending_topics():
    pn = request.args.get('pn', 'united_states')
    topics = get_trending_searches(pn=pn)
    return jsonify(topics)

@app.route('/api/keywords', methods=['GET'])
def get_keywords():
    keywords = TrackedKeyword.query.all()
    return jsonify([k.to_dict() for k in keywords])

@app.route('/api/keywords', methods=['POST'])
def add_keyword():
    data = request.get_json()
    if not data or 'keyword' not in data:
        return jsonify({'error': 'Keyword is required'}), 400

    new_keyword_str = data['keyword'].strip()
    if not new_keyword_str:
        return jsonify({'error': 'Keyword cannot be empty'}), 400

    existing_keyword = TrackedKeyword.query.filter_by(keyword=new_keyword_str).first()
    if existing_keyword:
        return jsonify({'error': 'Keyword already tracked'}), 409 # Conflict

    new_keyword = TrackedKeyword(keyword=new_keyword_str)
    db.session.add(new_keyword)
    db.session.commit()
    return jsonify(new_keyword.to_dict()), 201

@app.route('/api/keywords/<int:id>', methods=['DELETE'])
def delete_keyword(id):
    keyword = TrackedKeyword.query.get(id)
    if keyword is None:
        return jsonify({'error': 'Keyword not found'}), 404

    db.session.delete(keyword)
    db.session.commit()
    return jsonify({'message': 'Keyword deleted successfully'}), 200

@app.route('/api/keywords/<int:id>/interest', methods=['GET'])
def get_keyword_interest(id):
    keyword = TrackedKeyword.query.get(id)
    if keyword is None:
        return jsonify({'error': 'Keyword not found'}), 404

    interest_data = get_interest_over_time(keywords=[keyword.keyword])
    return jsonify(interest_data)

@app.route('/api/seo-dashboard/keyword/<int:id>', methods=['GET'])
def get_seo_dashboard_data(id):
    keyword = TrackedKeyword.query.get(id)
    if keyword is None:
        return jsonify({'error': 'Keyword not found'}), 404

    interest_data = get_interest_over_time(keywords=[keyword.keyword])
    rank_data = semrush_service.get_organic_positions(None, None, keyword.keyword, None, None)

    if not interest_data:
        return jsonify([])

    # Convert to DataFrames for easier merging
    interest_df = pd.DataFrame(interest_data)
    interest_df['date'] = pd.to_datetime(interest_df['date'])
    interest_df = interest_df.set_index('date')

    if not rank_data:
        # If there's no rank data, just return the interest data
        return jsonify(interest_data)

    rank_df = pd.DataFrame(rank_data)
    rank_df['date'] = pd.to_datetime(rank_df['date'])
    rank_df = rank_df.set_index('date')

    # Merge the two dataframes on the date index
    combined_df = interest_df.join(rank_df, how='outer').fillna(0)
    combined_df = combined_df.reset_index()

    # Convert back to list of dictionaries
    combined_data = combined_df.to_dict('records')

    return jsonify(combined_data)

@app.route('/api/posts', methods=['GET'])
def get_posts():
    posts = BlogPost.query.order_by(BlogPost.scheduled_time.desc()).all()
    return jsonify([p.to_dict() for p in posts])

@app.route('/api/posts', methods=['POST'])
def create_post():
    data = request.get_json()
    if not data or not data.get('title') or not data.get('topic'):
        return jsonify({'error': 'Title and topic are required'}), 400

    post = BlogPost(
        title=data['title'],
        topic=data['topic'],
        content=data.get('content', '')
    )
    db.session.add(post)
    db.session.commit()
    return jsonify(post.to_dict()), 201

@app.route('/api/posts/<int:id>', methods=['PUT'])
def update_post(id):
    post = BlogPost.query.get(id)
    if not post:
        return jsonify({'error': 'Post not found'}), 404

    data = request.get_json()
    new_status = data.get('status')

    if new_status == 'scheduled' and post.status != 'scheduled':
        if not data.get('scheduled_time'):
            return jsonify({'error': 'A scheduled_time is required to schedule a post.'}), 400

        integration = post.platform
        if integration and integration.platform_name == 'wordpress':
            wp_response = wordpress_service.schedule_post_on_wordpress(
                site_id=integration.site_url,
                token=integration.api_key,
                title=data.get('title', post.title),
                content=data.get('content', post.content),
                scheduled_date=parser.parse(data['scheduled_time'])
            )
            if not wp_response or wp_response.get('status') != 'success':
                return jsonify({'error': 'Failed to schedule post on WordPress.'}), 500

    post.title = data.get('title', post.title)
    post.topic = data.get('topic', post.topic)
    post.content = data.get('content', post.content)
    post.status = new_status if new_status else post.status

    if data.get('scheduled_time'):
        post.scheduled_time = parser.parse(data['scheduled_time'])

    db.session.commit()
    return jsonify(post.to_dict())

@app.route('/api/posts/<int:id>', methods=['DELETE'])
def delete_post(id):
    post = BlogPost.query.get(id)
    if not post:
        return jsonify({'error': 'Post not found'}), 404

    db.session.delete(post)
    db.session.commit()
    return jsonify({'message': 'Post deleted successfully'})

@app.route('/api/recommendations', methods=['GET'])
def get_recommendations():
    topic = request.args.get('topic')
    if not topic:
        return jsonify({'error': 'A topic query parameter is required.'}), 400

    historical_data = get_historical_interest(keywords=[topic], years=1)
    if not historical_data:
        return jsonify({'error': 'Could not retrieve trend data for this topic.'}), 404

    recommendation = recommendation_service.recommend_publishing_time(historical_data, topic)

    if not recommendation:
        return jsonify({'error': 'Could not generate a recommendation for this topic.'}), 404

    return jsonify(recommendation)

# --- New Product Forecaster API Routes ---

@app.route('/api/products', methods=['GET'])
def get_products():
    products = Product.query.all()
    return jsonify([p.to_dict() for p in products])

@app.route('/api/products', methods=['POST'])
def add_product():
    data = request.get_json()
    if not data or not data.get('name'):
        return jsonify({'error': 'Product name is required'}), 400

    product = Product(
        name=data['name'],
        category=data.get('category')
    )
    db.session.add(product)
    db.session.commit()
    return jsonify(product.to_dict()), 201

@app.route('/api/products/<int:id>', methods=['DELETE'])
def delete_product(id):
    product = Product.query.get(id)
    if not product:
        return jsonify({'error': 'Product not found'}), 404

    db.session.delete(product)
    db.session.commit()
    return jsonify({'message': 'Product deleted successfully'})

@app.route('/api/products/<int:id>/forecast', methods=['GET'])
def get_product_forecast(id):
    product = Product.query.get(id)
    if not product:
        return jsonify({'error': 'Product not found'}), 404

    historical_data = get_interest_over_time(keywords=[product.name])
    if not historical_data:
        return jsonify({'error': 'Could not retrieve trend data for this product.'}), 404

    sales_data = shopify_service.get_sales_history(None, None, product.id)
    sales_orders = sales_data['orders'] if sales_data and 'orders' in sales_data else []

    forecast_data = forecasting_service.generate_forecast(historical_data, sales_orders, product.name)

    return jsonify({
        'historical': historical_data,
        'forecast': forecast_data
    })

@app.route('/api/products/import-from-shopify', methods=['POST'])
def import_from_shopify():
    # In a real app, we'd get credentials from the DB for the current user
    # For now, we call the mocked service directly.
    shopify_data = shopify_service.get_shopify_products(store_name=None, access_token=None)

    if not shopify_data or 'products' not in shopify_data:
        return jsonify({'error': 'Failed to fetch products from Shopify.'}), 500

    imported_count = 0
    skipped_count = 0

    for shopify_product in shopify_data['products']:
        existing_product = Product.query.filter_by(name=shopify_product['title']).first()
        if not existing_product:
            new_product = Product(
                name=shopify_product['title'],
                category=shopify_product.get('product_type')
            )
            db.session.add(new_product)
            imported_count += 1
        else:
            skipped_count += 1

    db.session.commit()

    return jsonify({
        'message': 'Import complete.',
        'imported': imported_count,
        'skipped': skipped_count
    })

# --- Dynamic Pricing API Routes ---

@app.route('/api/products/<int:id>/pricing-rule', methods=['GET'])
def get_product_pricing_rule(id):
    product = Product.query.get(id)
    if not product:
        return jsonify({'error': 'Product not found'}), 404

    if product.pricing_rule:
        return jsonify(product.pricing_rule.to_dict())
    else:
        return jsonify(None)

@app.route('/api/pricing-rules', methods=['POST'])
def create_pricing_rule():
    data = request.get_json()
    if not data or not all(k in data for k in ['product_id', 'trend_threshold', 'price_adjustment_percentage']):
        return jsonify({'error': 'Missing required fields'}), 400

    existing_rule = PricingRule.query.filter_by(product_id=data['product_id']).first()
    if existing_rule:
        return jsonify({'error': 'A pricing rule for this product already exists'}), 409

    rule = PricingRule(
        product_id=data['product_id'],
        trend_threshold=data['trend_threshold'],
        price_adjustment_percentage=data['price_adjustment_percentage'],
        price_floor=data.get('price_floor'),
        price_ceiling=data.get('price_ceiling')
    )
    db.session.add(rule)
    db.session.commit()
    return jsonify(rule.to_dict()), 201

@app.route('/api/pricing-rules/<int:id>', methods=['PUT'])
def update_pricing_rule(id):
    rule = PricingRule.query.get(id)
    if not rule:
        return jsonify({'error': 'Pricing rule not found'}), 404

    data = request.get_json()
    rule.trend_threshold = data.get('trend_threshold', rule.trend_threshold)
    rule.price_adjustment_percentage = data.get('price_adjustment_percentage', rule.price_adjustment_percentage)
    rule.price_floor = data.get('price_floor', rule.price_floor)
    rule.price_ceiling = data.get('price_ceiling', rule.price_ceiling)

    db.session.commit()
    return jsonify(rule.to_dict())

@app.route('/api/pricing-rules/<int:id>', methods=['DELETE'])
def delete_pricing_rule(id):
    rule = PricingRule.query.get(id)
    if not rule:
        return jsonify({'error': 'Pricing rule not found'}), 404

    db.session.delete(rule)
    db.session.commit()
    return jsonify({'message': 'Pricing rule deleted successfully'})

@app.route('/api/products/<int:id>/dynamic-price', methods=['GET'])
def get_dynamic_price(id):
    dynamic_price_data = pricing_engine.calculate_dynamic_price(id)
    if not dynamic_price_data:
        return jsonify({'error': 'Could not calculate dynamic price. Ensure a pricing rule is set for this product.'}), 404
    return jsonify(dynamic_price_data)


if __name__ == '__main__':
    app.run(debug=True, port=5000)
