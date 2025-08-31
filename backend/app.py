from flask import Flask, jsonify, request
from trends_service import get_rising_queries

app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Hello, World!'

@app.route('/api/content-ideas')
def content_ideas():
    topic = request.args.get('topic')
    if not topic:
        return jsonify({"error": "A 'topic' query parameter is required."}), 400

    ideas = get_rising_queries(topic)
    return jsonify(ideas)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
