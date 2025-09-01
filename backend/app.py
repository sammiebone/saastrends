import os
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from sqlalchemy import Date, Text, DateTime
from dateutil import parser
from trends_service import get_rising_queries, get_trending_searches, get_interest_over_time, get_historical_interest
import semrush_service
import recommendation_service
import wordpress_service
import forecasting_service
import shopify_service

# App setup
app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))

# Database setup
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'app.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)

# --- Database Models ---

class TrackedKeyword(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    keyword = db.Column(db.String(100), nullable=False, unique=True)
    ranks = db.relationship('KeywordRank', backref='keyword', lazy=True, cascade="all, delete-orphan")

    def to_dict(self):
        return {
            'id': self.id,
            'keyword': self.keyword
        }

    def __repr__(self):
        return f'<TrackedKeyword {self.keyword}>'

class KeywordRank(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    rank = db.Column(db.Integer, nullable=False)
    domain = db.Column(db.String(255), nullable=False)
    tracked_keyword_id = db.Column(db.Integer, db.ForeignKey('tracked_keyword.id'), nullable=False)

    def __repr__(self):
        return f'<KeywordRank {self.keyword.keyword} - {self.date} - Rank: {self.rank}>'

class BlogPost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    topic = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(20), nullable=False, default='draft') # e.g., draft, scheduled, published
    scheduled_time = db.Column(db.DateTime, nullable=True)
    platform_integration_id = db.Column(db.Integer, db.ForeignKey('platform_integration.id'), nullable=True)

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'topic': self.topic,
            'content': self.content,
            'status': self.status,
            'scheduled_time': self.scheduled_time.isoformat() if self.scheduled_time else None,
            'platform_integration_id': self.platform_integration_id
        }

    def __repr__(self):
        return f'<BlogPost {self.title}>'

class PlatformIntegration(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    platform_name = db.Column(db.String(50), nullable=False) # 'wordpress', 'medium', etc.
    site_url = db.Column(db.String(255), nullable=False)
    api_key = db.Column(db.String(255), nullable=False) # For Application Passwords in WordPress
    posts = db.relationship('BlogPost', backref='platform', lazy=True)

    def __repr__(self):
        return f'<PlatformIntegration {self.platform_name} - {self.site_url}>'

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False, unique=True)
    category = db.Column(db.String(100), nullable=True)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'category': self.category
        }

    def __repr__(self):
        return f'<Product {self.name}>'

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
    combined_data = []
    if interest_data:
        for i, trend_point in enumerate(interest_data):
            rank = rank_data[i] if i < len(rank_data) else None
            combined_data.append({
                'date': trend_point.get('date'),
                'interest': trend_point.get(keyword.keyword),
                'rank': rank
            })
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

    forecast_data = forecasting_service.generate_forecast(historical_data, product.name)

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


if __name__ == '__main__':
    app.run(debug=True, port=5000)
