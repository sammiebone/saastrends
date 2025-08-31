import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import App from './App';

// Mock the global fetch function
global.fetch = jest.fn();

describe('ContentIdeaGenerator', () => {
  beforeEach(() => {
    fetch.mockClear();
  });

  test('renders the heading and form', () => {
    render(<App />);
    expect(screen.getByText('Content Idea Generator')).toBeInTheDocument();
    expect(screen.getByPlaceholderText("Enter a topic (e.g., 'AI')")).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Get Ideas' })).toBeInTheDocument();
  });

  test('fetches and displays ideas on form submission', async () => {
    const mockIdeas = [
      { query: 'ai in marketing', value: 150 },
      { query: 'future of ai', value: 120 },
    ];
    fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => mockIdeas,
    });

    render(<App />);

    // Simulate user input
    fireEvent.change(screen.getByPlaceholderText("Enter a topic (e.g., 'AI')"), {
      target: { value: 'AI' },
    });
    fireEvent.click(screen.getByRole('button', { name: 'Get Ideas' }));

    // Check for loading state
    expect(screen.getByRole('button', { name: 'Searching...' })).toBeInTheDocument();

    // Wait for the results to be displayed
    await waitFor(() => {
      expect(screen.getByText('ai in marketing')).toBeInTheDocument();
    });
    expect(screen.getByText('(Value: 150)')).toBeInTheDocument();
    expect(screen.getByText('future of ai')).toBeInTheDocument();
  });

  test('displays an error message if the fetch fails', async () => {
    fetch.mockRejectedValueOnce(new Error('Network response was not ok'));

    render(<App />);

    fireEvent.change(screen.getByPlaceholderText("Enter a topic (e.g., 'AI')"), {
      target: { value: 'API Failure' },
    });
    fireEvent.click(screen.getByRole('button', { name: 'Get Ideas' }));

    // Wait for the error message to be displayed
    await waitFor(() => {
      expect(screen.getByText('Failed to fetch ideas. Please try again later.')).toBeInTheDocument();
    });
  });

  test('displays an error message if no topic is entered', () => {
    render(<App />);
    fireEvent.click(screen.getByRole('button', { name: 'Get Ideas' }));
    expect(screen.getByText('Please enter a topic.')).toBeInTheDocument();
  });
});
