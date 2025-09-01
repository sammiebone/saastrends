import React, { useState, useEffect } from 'react';
import { Line } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
);

function KeywordTracker() {
  const [keywords, setKeywords] = useState([]);
  const [newKeyword, setNewKeyword] = useState('');
  const [selectedKeyword, setSelectedKeyword] = useState(null);
  const [chartData, setChartData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  // Fetch all tracked keywords on component mount
  useEffect(() => {
    const fetchKeywords = async () => {
      try {
        const response = await fetch('/api/keywords');
        const data = await response.json();
        setKeywords(data);
      } catch (e) {
        setError('Failed to load keywords.');
      }
    };
    fetchKeywords();
  }, []);

  // Fetch interest data when a keyword is selected
  useEffect(() => {
    if (!selectedKeyword) {
      setChartData(null);
      return;
    }

    const fetchInterestData = async () => {
      try {
        const response = await fetch(`/api/keywords/${selectedKeyword.id}/interest`);
        const data = await response.json();

        // Format data for Chart.js
        const labels = data.map(d => d.date);
        const values = data.map(d => d[selectedKeyword.keyword]);

        setChartData({
          labels,
          datasets: [
            {
              label: `Interest for "${selectedKeyword.keyword}"`,
              data: values,
              borderColor: 'rgb(75, 192, 192)',
              tension: 0.1,
            },
          ],
        });
      } catch (e) {
        setError(`Failed to load interest data for ${selectedKeyword.keyword}.`);
      }
    };

    fetchInterestData();
  }, [selectedKeyword]);

  const handleAddKeyword = async (e) => {
    e.preventDefault();
    if (!newKeyword.trim()) return;
    setLoading(true);
    try {
      const response = await fetch('/api/keywords', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ keyword: newKeyword }),
      });
      if (response.ok) {
        const addedKeyword = await response.json();
        setKeywords([...keywords, addedKeyword]);
        setNewKeyword('');
      } else {
        const err = await response.json();
        setError(err.error || 'Failed to add keyword.');
      }
    } catch (e) {
      setError('Failed to add keyword.');
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteKeyword = async (id) => {
    try {
      await fetch(`/api/keywords/${id}`, { method: 'DELETE' });
      setKeywords(keywords.filter(k => k.id !== id));
      if (selectedKeyword && selectedKeyword.id === id) {
        setSelectedKeyword(null);
      }
    } catch (e) {
      setError('Failed to delete keyword.');
    }
  };

  return (
    <div className="feature-container">
      <h2>Keyword Performance Tracker</h2>

      <div className="keyword-manager">
        <div className="keyword-list">
          <h3>Tracked Keywords</h3>
          <ul>
            {keywords.map(k => (
              <li key={k.id} className={selectedKeyword?.id === k.id ? 'selected' : ''}>
                <span onClick={() => setSelectedKeyword(k)}>{k.keyword}</span>
                <button onClick={() => handleDeleteKeyword(k.id)}>Delete</button>
              </li>
            ))}
          </ul>
        </div>

        <form onSubmit={handleAddKeyword}>
          <input
            type="text"
            value={newKeyword}
            onChange={(e) => setNewKeyword(e.target.value)}
            placeholder="Add a new keyword"
          />
          <button type="submit" disabled={loading}>
            {loading ? 'Adding...' : 'Add Keyword'}
          </button>
        </form>
      </div>

      {error && <p className="error">{error}</p>}

      <div className="chart-container">
        {selectedKeyword && chartData ? (
          <Line data={chartData} options={{ responsive: true, plugins: { title: { display: true, text: `Interest Over Time` }}}} />
        ) : (
          <p>{selectedKeyword ? 'Loading chart data...' : 'Select a keyword to see its trend.'}</p>
        )}
      </div>
    </div>
  );
}

export default KeywordTracker;
