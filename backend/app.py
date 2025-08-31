from flask import Flask, jsonify, request
from trends_service import get_rising_queries, get_trending_searches

app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Hello, World!'

@app.route('/api/content-ideas')
def content_ideas():
    topic = request.args.get('topic')
    if not topic:
        return jsonify({"error": "A 'topic' query parameter is required."}), 400

    # Get filter parameters from the query string, with defaults
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
    # Get the country parameter from the query string, default to 'united_states'
    pn = request.args.get('pn', 'united_states')
    topics = get_trending_searches(pn=pn)
    return jsonify(topics)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
