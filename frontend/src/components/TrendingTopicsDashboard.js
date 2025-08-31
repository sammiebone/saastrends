import React, { useState, useEffect } from 'react';

function TrendingTopicsDashboard() {
  const [trends, setTrends] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [country, setCountry] = useState('united_states');

  useEffect(() => {
    const fetchTrends = async () => {
      setLoading(true);
      setError('');
      try {
        const response = await fetch(`/api/trending-topics?pn=${country}`);
        if (!response.ok) {
          throw new Error('Network response was not ok');
        }
        const data = await response.json();
        setTrends(data);
      } catch (error) {
        setError('Failed to fetch trending topics.');
        console.error('Error fetching data:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchTrends();
  }, [country]); // Re-run effect when country changes

  return (
    <div className="feature-container">
      <h2>Trending Topics Dashboard</h2>
      <div className="filters">
        <label htmlFor="country-select">Country:</label>
        <select
          id="country-select"
          value={country}
          onChange={(e) => setCountry(e.target.value)}
        >
          <option value="united_states">United States</option>
          <option value="japan">Japan</option>
          <option value="great_britain">Great Britain</option>
          <option value="australia">Australia</option>
          <option value="canada">Canada</option>
        </select>
      </div>
      <div className="dashboard">
        {loading && <p>Loading trends...</p>}
        {error && <p className="error">{error}</p>}
        {!loading && !error && (
          <ul>
            {trends.map((trend, index) => (
              <li key={index}>{trend}</li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
}

export default TrendingTopicsDashboard;
