import React, { useState, useEffect } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

const InventoryManager = () => {
    const [products, setProducts] = useState([]);
    const [selectedProduct, setSelectedProduct] = useState('');
    const [chartData, setChartData] = useState([]);
    const [inventoryLevel, setInventoryLevel] = useState(null);
    const [recommendation, setRecommendation] = useState('');

    useEffect(() => {
        // Fetch products for the dropdown
        fetch('/api/products')
            .then(res => res.json())
            .then(data => {
                setProducts(data.products);
                if (data.products.length > 0) {
                    setSelectedProduct(data.products[0].id);
                }
            })
            .catch(error => console.error('Error fetching products:', error));
    }, []);

    useEffect(() => {
        if (selectedProduct) {
            // Fetch forecast and inventory data when a product is selected
            fetch(`/api/inventory/forecast/${selectedProduct}`)
                .then(res => res.json())
                .then(data => {
                    // Combine historical, sales, and forecast data for the chart
                    const combinedData = [
                        ...data.historical_trends,
                        ...data.sales_history,
                        ...data.forecast,
                    ].map(item => ({
                        date: item.date,
                        trends: item.value,
                        sales: item.quantity,
                        forecast: item.forecast_value,
                    }));

                    setChartData(combinedData);
                    setInventoryLevel(data.inventory_level);
                    generateRecommendation(data.forecast, data.inventory_level);
                })
                .catch(error => console.error('Error fetching forecast data:', error));
        }
    }, [selectedProduct]);

    const generateRecommendation = (forecast, currentInventory) => {
        if (!forecast || forecast.length === 0 || currentInventory === null) {
            setRecommendation('');
            return;
        }

        const upwardTrend = forecast[forecast.length - 1].forecast_value > forecast[0].forecast_value;
        const lowStock = currentInventory < 50; // Example threshold

        if (upwardTrend && lowStock) {
            setRecommendation('Strong upward trend and low stock. Recommend reordering soon.');
        } else if (upwardTrend) {
            setRecommendation('Upward trend detected. Monitor stock levels closely.');
        } else if (lowStock) {
            setRecommendation('Stock is low. Consider reordering.');
        } else {
            setRecommendation('Stock levels and trends appear stable.');
        }
    };

    return (
        <div>
            <h2>Inventory Management</h2>
            <select onChange={(e) => setSelectedProduct(e.target.value)} value={selectedProduct}>
                {products.map(product => (
                    <option key={product.id} value={product.id}>{product.title}</option>
                ))}
            </select>

            {chartData.length > 0 && (
                <ResponsiveContainer width="100%" height={400}>
                    <LineChart data={chartData}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="date" />
                        <YAxis />
                        <Tooltip />
                        <Legend />
                        <Line type="monotone" dataKey="trends" stroke="#8884d8" name="Google Trends" />
                        <Line type="monotone" dataKey="sales" stroke="#82ca9d" name="Sales" />
                        <Line type="monotone" dataKey="forecast" stroke="#ffc658" name="Forecast" strokeDasharray="5 5" />
                    </LineChart>
                </ResponsiveContainer>
            )}

            {inventoryLevel !== null && (
                <div>
                    <h3>Current Inventory Level: {inventoryLevel}</h3>
                    <p><strong>Recommendation:</strong> {recommendation}</p>
                </div>
            )}
        </div>
    );
};

export default InventoryManager;
