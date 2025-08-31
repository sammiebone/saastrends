import React, { useState } from 'react';

function ContentIdeaGenerator() {
  const [topic, setTopic] = useState('');
  const [ideas, setIdeas] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const fetchIdeas = async (e) => {
    e.preventDefault();
    if (!topic) {
      setError('Please enter a topic.');
      return;
    }
    setLoading(true);
    setError('');
    setIdeas([]);

    try {
      const response = await fetch(`/api/content-ideas?topic=${encodeURIComponent(topic)}`);
      if (!response.ok) {
        throw new Error('Network response was not ok');
      }
      const data = await response.json();
      if (data.error) {
          setError(data.error);
          setIdeas([]);
      } else {
        setIdeas(data);
      }
    } catch (error) {
      setError('Failed to fetch ideas. Please try again later.');
      console.error('Error fetching data:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="feature-container">
      <h2>Content Idea Generator</h2>
      <form onSubmit={fetchIdeas}>
        <input
          type="text"
          value={topic}
          onChange={(e) => setTopic(e.target.value)}
          placeholder="Enter a topic (e.g., 'AI')"
        />
        <button type="submit" disabled={loading}>
          {loading ? 'Searching...' : 'Get Ideas'}
        </button>
      </form>

      {error && <p className="error">{error}</p>}

      <div className="results">
        {ideas.length > 0 && (
          <ul>
            {ideas.map((idea, index) => (
              <li key={index}>
                <strong>{idea.query}</strong> (Value: {idea.value})
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
}

export default ContentIdeaGenerator;
