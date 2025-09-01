import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import KeywordTracker from './KeywordTracker';

// Mock the global fetch function
global.fetch = jest.fn();

// Mock the Chart.js component
jest.mock('react-chartjs-2', () => ({
  Line: () => <canvas data-testid="line-chart" />
}));

describe('KeywordTracker', () => {
  beforeEach(() => {
    fetch.mockClear();
  });

  test('renders the component and fetches initial keywords', async () => {
    fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => [{ id: 1, keyword: 'SaaS' }],
    });

    render(<KeywordTracker />);

    expect(screen.getByText('Keyword Performance Tracker')).toBeInTheDocument();

    await waitFor(() => {
      expect(screen.getByText('SaaS')).toBeInTheDocument();
    });
    expect(fetch).toHaveBeenCalledWith('/api/keywords');
  });

  test('adds a new keyword to the list', async () => {
    // Initial fetch is empty
    fetch.mockResolvedValueOnce({ ok: true, json: async () => [] });

    render(<KeywordTracker />);

    // Mock the POST request for adding a new keyword
    fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ id: 2, keyword: 'Fintech' }),
    });

    fireEvent.change(screen.getByPlaceholderText('Add a new keyword'), {
      target: { value: 'Fintech' },
    });
    fireEvent.click(screen.getByRole('button', { name: 'Add Keyword' }));

    await waitFor(() => {
      expect(screen.getByText('Fintech')).toBeInTheDocument();
    });
    expect(fetch).toHaveBeenCalledWith('/api/keywords', expect.any(Object));
  });

  test('deletes a keyword from the list', async () => {
    fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => [{ id: 1, keyword: 'SaaS' }],
    });

    render(<KeywordTracker />);

    await waitFor(() => expect(screen.getByText('SaaS')).toBeInTheDocument());

    // Mock the DELETE request
    fetch.mockResolvedValueOnce({ ok: true });

    fireEvent.click(screen.getByRole('button', { name: 'Delete' }));

    await waitFor(() => {
      expect(screen.queryByText('SaaS')).not.toBeInTheDocument();
    });
  });

  test('selects a keyword and displays the chart', async () => {
    fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => [{ id: 1, keyword: 'SaaS' }],
    });

    render(<KeywordTracker />);

    await waitFor(() => expect(screen.getByText('SaaS')).toBeInTheDocument());

    // Mock the fetch for interest data
    fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => [{ date: '2023-01-01', SaaS: 100 }],
    });

    fireEvent.click(screen.getByText('SaaS'));

    await waitFor(() => {
      expect(screen.getByTestId('line-chart')).toBeInTheDocument();
    });
    expect(fetch).toHaveBeenCalledWith('/api/keywords/1/interest');
  });
});
