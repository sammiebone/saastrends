import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import App from './App';

// Mock the child components to isolate the App component's logic
jest.mock('./components/TrendingTopicsDashboard', () => () => <div>Trending Topics Dashboard Mock</div>);
jest.mock('./components/ContentIdeaGenerator', () => () => <div>Content Idea Generator Mock</div>);
jest.mock('./components/KeywordTracker', () => () => <div>Keyword Tracker Mock</div>);
jest.mock('./components/SeoDashboard', () => () => <div>SEO Dashboard Mock</div>);

describe('App Container', () => {
  test('renders the Trending Dashboard by default', () => {
    render(<App />);
    expect(screen.getByText('Trending Topics Dashboard Mock')).toBeInTheDocument();
    expect(screen.queryByText('Content Idea Generator Mock')).not.toBeInTheDocument();
  });

  test('switches to the Content Idea Generator view on button click', () => {
    render(<App />);

    // Click the button to switch views
    const generatorButton = screen.getByRole('button', { name: 'Content Idea Generator' });
    fireEvent.click(generatorButton);

    // Assert the view has changed
    expect(screen.getByText('Content Idea Generator Mock')).toBeInTheDocument();
    expect(screen.queryByText('Trending Topics Dashboard Mock')).not.toBeInTheDocument();
  });

  test('switches back to the Trending Dashboard view', () => {
    render(<App />);

    // Switch to generator view first
    const generatorButton = screen.getByRole('button', { name: 'Content Idea Generator' });
    fireEvent.click(generatorButton);
    expect(screen.getByText('Content Idea Generator Mock')).toBeInTheDocument();

    // Switch back to dashboard view
    const dashboardButton = screen.getByRole('button', { name: 'Trending Dashboard' });
    fireEvent.click(dashboardButton);

    // Assert the view has switched back
    expect(screen.getByText('Trending Topics Dashboard Mock')).toBeInTheDocument();
    expect(screen.queryByText('Content Idea Generator Mock')).not.toBeInTheDocument();
  });

  test('switches to the Keyword Tracker view on button click', () => {
    render(<App />);

    const trackerButton = screen.getByRole('button', { name: 'Keyword Tracker' });
    fireEvent.click(trackerButton);

    expect(screen.getByText('Keyword Tracker Mock')).toBeInTheDocument();
    expect(screen.queryByText('Trending Topics Dashboard Mock')).not.toBeInTheDocument();
    expect(screen.queryByText('Content Idea Generator Mock')).not.toBeInTheDocument();
  });

  test('switches to the SEO Dashboard view on button click', () => {
    render(<App />);

    const seoButton = screen.getByRole('button', { name: 'SEO Dashboard' });
    fireEvent.click(seoButton);

    expect(screen.getByText('SEO Dashboard Mock')).toBeInTheDocument();
  });
});
