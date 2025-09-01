import React, { useState, useEffect } from 'react';
import { Line } from 'react-chartjs-2';

// Chart.js is already registered in other components, but it's good practice
// to ensure it's registered here for standalone use.
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

function ProductForecaster() {
  const [products, setProducts] = useState([]);
  const [selectedProductId, setSelectedProductId] = useState('');
  const [chartData, setChartData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  // Fetch all products on component mount
  useEffect(() => {
    const fetchProducts = async () => {
      try {
        const response = await fetch('/api/products');
        const data = await response.json();
        setProducts(data);
        if (data.length > 0) {
          setSelectedProductId(data[0].id);
        }
      } catch (e) {
        setError('Failed to load products.');
      }
    };
    fetchProducts();
  }, []);

  // Fetch forecast data when a product is selected
  useEffect(() => {
    if (!selectedProductId) {
      setChartData(null);
      return;
    }

    const fetchForecastData = async () => {
      setLoading(true);
      setError('');
      try {
        const response = await fetch(`/api/products/${selectedProductId}/forecast`);
        const data = await response.json();
        const selectedProduct = products.find(p => p.id === parseInt(selectedProductId));

        // Format data for Chart.js
        const historicalLabels = data.historical.map(d => d.date);
        const historicalValues = data.historical.map(d => d[selectedProduct.name]);

        const forecastLabels = data.forecast.map(d => d.date);
        const forecastValues = data.forecast.map(d => d.forecast_value);

        const allLabels = [...historicalLabels, ...forecastLabels];

        setChartData({
          labels: allLabels,
          datasets: [
            {
              label: `Historical Interest for "${selectedProduct?.name}"`,
              data: historicalValues,
              borderColor: 'rgb(75, 192, 192)',
              tension: 0.1,
            },
            {
              label: `Forecasted Interest for "${selectedProduct?.name}"`,
              data: [...new Array(historicalValues.length).fill(null), ...forecastValues],
              borderColor: 'rgb(255, 99, 132)',
              borderDash: [5, 5], // Dashed line for forecast
              tension: 0.1,
            },
          ],
        });
      } catch (e) {
        setError('Failed to load forecast data.');
      } finally {
        setLoading(false);
      }
    };

    fetchForecastData();
  }, [selectedProductId, products]);

  const handleImport = async () => {
      alert("Importing products from Shopify... (mocked)");
      // In a real app, this would trigger the import and then refetch products
      const response = await fetch('/api/products/import-from-shopify', { method: 'POST' });
      const result = await response.json();
      alert(`${result.imported} products imported, ${result.skipped} skipped.`);
      // Refetch products list
      const res = await fetch('/api/products');
      const data = await res.json();
      setProducts(data);
  };

  return (
    <div className="feature-container">
      <h2>Product Trend Forecaster</h2>
      <div className="controls">
        <div className="filters">
          <label htmlFor="product-select">Select Product:</label>
          <select
            id="product-select"
            value={selectedProductId}
            onChange={(e) => setSelectedProductId(e.target.value)}
          >
            <option value="">--Select a Product--</option>
            {products.map(p => (
              <option key={p.id} value={p.id}>{p.name}</option>
            ))}
          </select>
        </div>
        <button onClick={handleImport}>Import from Shopify (Mock)</button>
      </div>

      {error && <p className="error">{error}</p>}

      <div className="chart-container">
        {loading && <p>Loading chart data...</p>}
        {!loading && chartData ? (
          <Line data={chartData} options={{ responsive: true, plugins: { title: { display: true, text: `Product Interest and Forecast` }}}} />
        ) : (
          !loading && <p>Select a product to see its forecast.</p>
        )}
      </div>
    </div>
  );
}

export default ProductForecaster;
