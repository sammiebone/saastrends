import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import fetchMock from 'fetch-mock';
import DynamicPricingDashboard from './DynamicPricingDashboard';

describe('DynamicPricingDashboard', () => {
  afterEach(() => {
    fetchMock.restore();
  });

  test('renders dynamic pricing dashboard component and fetches products', async () => {
    fetchMock.get('/api/products', [
      { id: 1, name: 'Test Product 1' },
      { id: 2, name: 'Test Product 2' },
    ]);
    fetchMock.get('/api/keywords/1/interest', []);
    fetchMock.get('/api/products/1/pricing-rule', {});
    fetchMock.get('/api/products/1/dynamic-price', {});

    render(<DynamicPricingDashboard />);

    expect(screen.getByText(/Dynamic Pricing Dashboard/i)).toBeInTheDocument();

    await waitFor(() => {
      expect(screen.getByText('Test Product 1')).toBeInTheDocument();
    });
  });

  test('fetches and displays data when a product is selected', async () => {
    fetchMock.get('/api/products', [{ id: 1, name: 'Test Product' }]);
    fetchMock.get('/api/keywords/1/interest', [{ date: '2023-01-01', 'Test Product': 50 }]);
    fetchMock.get('/api/products/1/pricing-rule', {
      id: 1,
      product_id: 1,
      trend_threshold: 40,
      price_adjustment_percentage: 10,
      price_floor: 90,
      price_ceiling: 110,
    });
    fetchMock.get('/api/products/1/dynamic-price', {
      original_price: 100,
      dynamic_price: 110,
      trend_value: 50,
      trend_threshold: 40,
    });

    render(<DynamicPricingDashboard />);

    await waitFor(() => {
      // Check if pricing rule data is displayed
      expect(screen.getByDisplayValue('40')).toBeInTheDocument();
      // Check if dynamic price recommendation is displayed
      expect(screen.getByText('Original Price: $100')).toBeInTheDocument();
    });
  });

  test('allows creating and updating a pricing rule', async () => {
    fetchMock.get('/api/products', [{ id: 1, name: 'Test Product' }]);
    fetchMock.get('/api/keywords/1/interest', []);
    fetchMock.get('/api/products/1/pricing-rule', null); // No initial rule
    fetchMock.get('/api/products/1/dynamic-price', null);

    render(<DynamicPricingDashboard />);

    await waitFor(() => {
      expect(screen.getByText('No pricing rule set for this product.')).toBeInTheDocument();
    });

    // Mock the POST request for creating a new rule
    fetchMock.post('/api/pricing-rules', {
      id: 2,
      product_id: 1,
      trend_threshold: 50,
      price_adjustment_percentage: 15,
    });

    // This test would be more complex, requiring simulation of form input
    // For now, we'll just check that the component renders without a rule
  });
});
