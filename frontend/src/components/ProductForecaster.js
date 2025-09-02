import React, { useState, useEffect } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

const ProductForecaster = () => {
    const [products, setProducts] = useState([]);
    const [selectedProduct, setSelectedProduct] = useState('');
    const [forecastData, setForecastData] = useState(null);

    useEffect(() => {
        // Fetch products for the dropdown
        fetch('/api/products')
            .then(res => res.json())
            .then(data => {
                if (Array.isArray(data)) {
                    setProducts(data);
                    if (data.length > 0) {
                        setSelectedProduct(data[0].id);
                    }
                }
            })
            .catch(error => console.error('Error fetching products:', error));
    }, []);

    useEffect(() => {
        if (selectedProduct) {
            // Fetch forecast data when a product is selected
            fetch(`/api/products/${selectedProduct}/forecast`)
                .then(res => res.json())
                .then(data => setForecastData(data))
                .catch(error => console.error('Error fetching forecast data:', error));
        }
    }, [selectedProduct]);

    const formatChartData = () => {
        if (!forecastData) return [];

        const combined = [
            ...forecastData.historical.map(h => ({ date: h.date, value: h[products.find(p=>p.id === selectedProduct)?.name], type: 'Historical' })),
            ...forecastData.forecast.map(f => ({ date: f.date, value: f.forecast_value, type: 'Forecast' }))
        ];

        return combined;
    };

    return (
        <div>
            <h2>Product Trend Forecaster</h2>
            <select onChange={(e) => setSelectedProduct(e.target.value)} value={selectedProduct}>
                {products.map(product => (
                    <option key={product.id} value={product.id}>{product.name}</option>
                ))}
            </select>

            {forecastData && (
                <ResponsiveContainer width="100%" height={400}>
                    <LineChart data={formatChartData()}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="date" />
                        <YAxis />
                        <Tooltip />
                        <Legend />
                        <Line type="monotone" dataKey="value" stroke="#8884d8" name="Trend" />
                    </LineChart>
                </ResponsiveContainer>
            )}
        </div>
    );
};

export default ProductForecaster;
