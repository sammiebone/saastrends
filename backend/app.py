import os
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from trends_service import get_rising_queries, get_trending_searches, get_interest_over_time

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

    def to_dict(self):
        return {
            'id': self.id,
            'keyword': self.keyword
        }

    def __repr__(self):
        return f'<TrackedKeyword {self.keyword}>'

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

# --- New Keyword Management API Routes ---

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

    # For now, we only fetch data for the single keyword.
    # The service supports multiple, so this could be expanded later.
    interest_data = get_interest_over_time(keywords=[keyword.keyword])
    return jsonify(interest_data)


if __name__ == '__main__':
    app.run(debug=True, port=5000)
