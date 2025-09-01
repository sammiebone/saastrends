import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import ProductForecaster from './ProductForecaster';

// Mock the global fetch function
global.fetch = jest.fn();

// Mock the Chart.js component
jest.mock('react-chartjs-2', () => ({
  Line: () => <canvas data-testid="forecaster-line-chart" />
}));

describe('ProductForecaster', () => {
  beforeEach(() => {
    fetch.mockClear();
  });

  test('renders the component and fetches initial products', async () => {
    // Mock for fetching the product list
    fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => [{ id: 1, name: 'T-Shirt' }],
    });
    // Mock for fetching forecast data for the first product
    fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ historical: [], forecast: [] }),
    });

    render(<ProductForecaster />);

    expect(screen.getByText('Product Trend Forecaster')).toBeInTheDocument();

    await waitFor(() => {
      expect(screen.getByRole('option', { name: 'T-Shirt' })).toBeInTheDocument();
    });
    expect(fetch).toHaveBeenCalledWith('/api/products');
  });

  test('fetches and displays forecast data when a product is selected', async () => {
    // Mock for product list
    fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => [{ id: 1, name: 'T-Shirt' }],
    });

    render(<ProductForecaster />);
    await waitFor(() => expect(screen.getByRole('option', { name: 'T-Shirt' })).toBeInTheDocument());

    // Mock for the forecast data
    fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({
          historical: [{ date: '2023-01-01', 'T-Shirt': 50 }],
          forecast: [{ date: '2023-01-08', forecast_value: 55 }]
        }),
    });

    // Select the product
    fireEvent.change(screen.getByLabelText('Select Product:'), { target: { value: '1' } });

    await waitFor(() => {
      expect(screen.getByTestId('forecaster-line-chart')).toBeInTheDocument();
    });
    expect(fetch).toHaveBeenCalledWith('/api/products/1/forecast');
  });

  test('handles Shopify import button click', async () => {
    // Mock for initial product list
    fetch.mockResolvedValueOnce({ ok: true, json: async () => [] });
    render(<ProductForecaster />);

    // Mock for the import API call
    fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ imported: 1, skipped: 0 }),
    });
    // Mock for the refetch of products
    fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => [{id: 1, name: 'Imported Product'}]
    });

    const alertMock = jest.spyOn(window, 'alert').mockImplementation(() => {});

    fireEvent.click(screen.getByRole('button', { name: 'Import from Shopify (Mock)' }));

    await waitFor(() => {
        expect(fetch).toHaveBeenCalledWith('/api/products/import-from-shopify', expect.any(Object));
    });

    // Check for the second alert and the refetched product
    await waitFor(() => {
        expect(alertMock).toHaveBeenCalledWith('1 products imported, 0 skipped.');
        expect(screen.getByRole('option', {name: 'Imported Product'})).toBeInTheDocument();
    });

    alertMock.mockRestore();
  });
});
