import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import SeoDashboard from './SeoDashboard';

// Mock the global fetch function
global.fetch = jest.fn();

// Mock the Chart.js component
jest.mock('react-chartjs-2', () => ({
  Line: () => <canvas data-testid="seo-line-chart" />
}));

describe('SeoDashboard', () => {
  beforeEach(() => {
    fetch.mockClear();
  });

  test('renders and fetches keywords, then fetches dashboard data for the first keyword', async () => {
    // Mock for fetching the keyword list
    fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => [{ id: 1, keyword: 'SaaS' }, { id: 2, keyword: 'AI' }],
    });

    // Mock for fetching the dashboard data for the first keyword
    fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => [
        { date: '2023-01-01', interest: 50, rank: 10 },
        { date: '2023-01-02', interest: 55, rank: 9 },
      ],
    });

    render(<SeoDashboard />);

    expect(screen.getByText('SEO Dashboard')).toBeInTheDocument();

    // Wait for the keyword dropdown to be populated
    await waitFor(() => {
      expect(screen.getByRole('option', { name: 'SaaS' })).toBeInTheDocument();
    });

    // Wait for the chart to be displayed
    await waitFor(() => {
      expect(screen.getByTestId('seo-line-chart')).toBeInTheDocument();
    });

    // Check that the correct API calls were made
    expect(fetch).toHaveBeenCalledWith('/api/keywords');
    expect(fetch).toHaveBeenCalledWith('/api/seo-dashboard/keyword/1');
  });

  test('fetches new dashboard data when a different keyword is selected', async () => {
    // Mock for initial keyword list
    fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => [{ id: 1, keyword: 'SaaS' }, { id: 2, keyword: 'AI' }],
    });

    // Mock for first keyword's data
    fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => [],
    });

    render(<SeoDashboard />);

    // Wait for dropdown
    await waitFor(() => expect(screen.getByRole('option', { name: 'AI' })).toBeInTheDocument());

    // Mock for second keyword's data
    fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => [{ date: '2023-01-01', interest: 80, rank: 5 }],
    });

    // Select the second keyword
    fireEvent.change(screen.getByLabelText('Select Keyword:'), {
      target: { value: '2' },
    });

    // Wait for chart
    await waitFor(() => expect(screen.getByTestId('seo-line-chart')).toBeInTheDocument());

    // Check that the API was called for the second keyword
    expect(fetch).toHaveBeenCalledWith('/api/seo-dashboard/keyword/2');
  });
});
