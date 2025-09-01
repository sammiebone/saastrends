import React, { useState, useEffect } from 'react';
import { Line } from 'react-chartjs-2';

// Chart.js is already registered in KeywordTracker.js, but it's good practice
// to register it here as well in case this component is used independently.
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

function SeoDashboard() {
  const [keywords, setKeywords] = useState([]);
  const [selectedKeywordId, setSelectedKeywordId] = useState('');
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
        if (data.length > 0) {
          setSelectedKeywordId(data[0].id); // Select the first keyword by default
        }
      } catch (e) {
        setError('Failed to load keywords.');
      }
    };
    fetchKeywords();
  }, []);

  // Fetch dashboard data when a keyword is selected
  useEffect(() => {
    if (!selectedKeywordId) {
      setChartData(null);
      return;
    }

    const fetchDashboardData = async () => {
      setLoading(true);
      setError('');
      try {
        const response = await fetch(`/api/seo-dashboard/keyword/${selectedKeywordId}`);
        const data = await response.json();

        const selectedKeyword = keywords.find(k => k.id === parseInt(selectedKeywordId));

        // Format data for Chart.js
        const labels = data.map(d => d.date);
        const interestData = data.map(d => d.interest);
        const rankData = data.map(d => d.rank);

        setChartData({
          labels,
          datasets: [
            {
              label: `Interest for "${selectedKeyword?.keyword}"`,
              data: interestData,
              borderColor: 'rgb(75, 192, 192)',
              backgroundColor: 'rgba(75, 192, 192, 0.5)',
              yAxisID: 'y',
            },
            {
              label: `Rank for "${selectedKeyword?.keyword}"`,
              data: rankData,
              borderColor: 'rgb(255, 99, 132)',
              backgroundColor: 'rgba(255, 99, 132, 0.5)',
              yAxisID: 'y1',
            },
          ],
        });
      } catch (e) {
        setError('Failed to load dashboard data.');
      } finally {
        setLoading(false);
      }
    };

    fetchDashboardData();
  }, [selectedKeywordId, keywords]);

  const chartOptions = {
    responsive: true,
    interaction: {
      mode: 'index',
      intersect: false,
    },
    stacked: false,
    plugins: {
      title: {
        display: true,
        text: 'Keyword Interest vs. Rank',
      },
    },
    scales: {
      y: {
        type: 'linear',
        display: true,
        position: 'left',
        title: {
          display: true,
          text: 'Google Trends Interest'
        }
      },
      y1: {
        type: 'linear',
        display: true,
        position: 'right',
        title: {
          display: true,
          text: 'SEMrush Rank'
        },
        reverse: true, // Lower rank numbers are better
        grid: {
          drawOnChartArea: false, // only draw grid for y-axis
        },
      },
    },
  };

  return (
    <div className="feature-container">
      <h2>SEO Dashboard</h2>
      <div className="filters">
        <label htmlFor="keyword-select">Select Keyword:</label>
        <select
          id="keyword-select"
          value={selectedKeywordId}
          onChange={(e) => setSelectedKeywordId(e.target.value)}
        >
          <option value="">--Select a Keyword--</option>
          {keywords.map(k => (
            <option key={k.id} value={k.id}>{k.keyword}</option>
          ))}
        </select>
      </div>

      {error && <p className="error">{error}</p>}

      <div className="chart-container">
        {loading && <p>Loading chart data...</p>}
        {!loading && chartData ? (
          <Line options={chartOptions} data={chartData} />
        ) : (
          !loading && <p>Select a keyword to see the dashboard.</p>
        )}
      </div>
    </div>
  );
}

export default SeoDashboard;
