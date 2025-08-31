import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import TrendingTopicsDashboard from './TrendingTopicsDashboard';

// Mock the global fetch function
global.fetch = jest.fn();

describe('TrendingTopicsDashboard', () => {
  beforeEach(() => {
    fetch.mockClear();
  });

  test('renders the dashboard and fetches initial trends', async () => {
    const mockTrends = ['SaaS', 'AI', 'Fintech'];
    fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => mockTrends,
    });

    render(<TrendingTopicsDashboard />);

    // Check for loading state initially
    expect(screen.getByText('Loading trends...')).toBeInTheDocument();

    // Wait for the results to be displayed
    await waitFor(() => {
      expect(screen.getByText('SaaS')).toBeInTheDocument();
      expect(screen.getByText('AI')).toBeInTheDocument();
      expect(screen.getByText('Fintech')).toBeInTheDocument();
    });

    // Check that fetch was called for the default country
    expect(fetch).toHaveBeenCalledWith('/api/trending-topics?pn=united_states');
  });

  test('fetches new trends when country is changed', async () => {
    // Initial fetch for US
    fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ['US Trend 1'],
    });

    render(<TrendingTopicsDashboard />);

    // Wait for initial content to load
    await waitFor(() => screen.getByText('US Trend 1'));

    // Mock the next fetch for Japan
    const mockJapanTrends = ['Anime', 'Sushi'];
    fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => mockJapanTrends,
    });

    // Change the dropdown value
    fireEvent.change(screen.getByLabelText('Country:'), {
      target: { value: 'japan' },
    });

    // Check that new results are displayed
    await waitFor(() => {
      expect(screen.getByText('Anime')).toBeInTheDocument();
      expect(screen.getByText('Sushi')).toBeInTheDocument();
    });

    // Check that fetch was called with the new country
    expect(fetch).toHaveBeenCalledWith('/api/trending-topics?pn=japan');
    expect(fetch).toHaveBeenCalledTimes(2);
  });
});
