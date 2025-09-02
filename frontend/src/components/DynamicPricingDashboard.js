import React, { useState, useEffect } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

const DynamicPricingDashboard = () => {
    const [products, setProducts] = useState([]);
    const [selectedProduct, setSelectedProduct] = useState('');
    const [trendData, setTrendData] = useState([]);
    const [pricingRule, setPricingRule] = useState(null);
    const [dynamicPrice, setDynamicPrice] = useState(null);

    useEffect(() => {
        fetch('/api/products')
            .then(res => res.json())
            .then(data => {
                setProducts(data);
                if (data.length > 0) {
                    setSelectedProduct(data[0].id);
                }
            })
            .catch(error => console.error('Error fetching products:', error));
    }, []);

    useEffect(() => {
        if (selectedProduct) {
            // Fetch trend data
            fetch(`/api/keywords/${selectedProduct}/interest`)
                .then(res => res.json())
                .then(data => setTrendData(data))
                .catch(error => console.error('Error fetching trend data:', error));

            // Fetch pricing rule
            fetch(`/api/products/${selectedProduct}/pricing-rule`)
                .then(res => res.json())
                .then(data => setPricingRule(data))
                .catch(error => console.error('Error fetching pricing rule:', error));

            // Fetch dynamic price
            fetch(`/api/products/${selectedProduct}/dynamic-price`)
                .then(res => res.json())
                .then(data => setDynamicPrice(data))
                .catch(error => console.error('Error fetching dynamic price:', error));
        }
    }, [selectedProduct]);

    const handleRuleChange = (e) => {
        const { name, value } = e.target;
        setPricingRule({ ...pricingRule, [name]: value });
    };

    const handleSaveRule = () => {
        const url = pricingRule.id ? `/api/pricing-rules/${pricingRule.id}` : '/api/pricing-rules';
        const method = pricingRule.id ? 'PUT' : 'POST';

        fetch(url, {
            method: method,
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ ...pricingRule, product_id: selectedProduct })
        })
        .then(res => res.json())
        .then(data => setPricingRule(data))
        .catch(error => console.error('Error saving pricing rule:', error));
    };

    return (
        <div>
            <h2>Dynamic Pricing Dashboard</h2>
            <select onChange={(e) => setSelectedProduct(e.target.value)} value={selectedProduct}>
                {products.map(product => (
                    <option key={product.id} value={product.id}>{product.name}</option>
                ))}
            </select>

            {trendData.length > 0 && (
                <ResponsiveContainer width="100%" height={300}>
                    <LineChart data={trendData}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="date" />
                        <YAxis />
                        <Tooltip />
                        <Legend />
                        <Line type="monotone" dataKey={products.find(p => p.id === selectedProduct)?.name} stroke="#8884d8" />
                    </LineChart>
                </ResponsiveContainer>
            )}

            <div>
                <h3>Pricing Rule</h3>
                {pricingRule ? (
                    <div>
                        <label>Trend Threshold:</label>
                        <input type="number" name="trend_threshold" value={pricingRule.trend_threshold} onChange={handleRuleChange} />
                        <label>Price Adjustment (%):</label>
                        <input type="number" name="price_adjustment_percentage" value={pricingRule.price_adjustment_percentage} onChange={handleRuleChange} />
                        <label>Price Floor:</label>
                        <input type="number" name="price_floor" value={pricingRule.price_floor || ''} onChange={handleRuleChange} />
                        <label>Price Ceiling:</label>
                        <input type="number" name="price_ceiling" value={pricingRule.price_ceiling || ''} onChange={handleRuleChange} />
                        <button onClick={handleSaveRule}>Save Rule</button>
                    </div>
                ) : (
                    <p>No pricing rule set for this product.</p>
                )}
            </div>

            {dynamicPrice && (
                <div>
                    <h3>Dynamic Price Recommendation</h3>
                    <p>Original Price: ${dynamicPrice.original_price}</p>
                    <p>Dynamic Price: ${dynamicPrice.dynamic_price}</p>
                    <p>(Based on trend value of {dynamicPrice.trend_value} vs. threshold of {dynamicPrice.trend_threshold})</p>
                </div>
            )}
        </div>
    );
};

export default DynamicPricingDashboard;
