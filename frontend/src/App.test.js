import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import App from './App';

// Mock the child components to isolate the App component's logic
jest.mock('./components/TrendingTopicsDashboard', () => () => <div>Trending Topics Dashboard Mock</div>);
jest.mock('./components/ContentIdeaGenerator', () => () => <div>Content Idea Generator Mock</div>);
jest.mock('./components/KeywordTracker', () => () => <div>Keyword Tracker Mock</div>);
jest.mock('./components/SeoDashboard', () => () => <div>SEO Dashboard Mock</div>);
jest.mock('./components/Scheduler', () => () => <div>Scheduler Mock</div>);
jest.mock('./components/ProductForecaster', () => () => <div>Product Forecaster Mock</div>);
jest.mock('./components/InventoryManager', () => () => <div>Inventory Manager Mock</div>);
jest.mock('./components/DynamicPricingDashboard', () => () => <div>Dynamic Pricing Dashboard Mock</div>);

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

  test('switches to the Content Scheduler view on button click', () => {
    render(<App />);

    const schedulerButton = screen.getByRole('button', { name: 'Content Scheduler' });
    fireEvent.click(schedulerButton);

    expect(screen.getByText('Scheduler Mock')).toBeInTheDocument();
  });

  test('switches to the Product Forecaster view on button click', () => {
    render(<App />);

    const forecasterButton = screen.getByRole('button', { name: 'Product Forecaster' });
    fireEvent.click(forecasterButton);

    expect(screen.getByText('Product Forecaster Mock')).toBeInTheDocument();
  });

  test('switches to the Inventory Manager view on button click', () => {
    render(<App />);

    const inventoryButton = screen.getByRole('button', { name: 'Inventory Manager' });
    fireEvent.click(inventoryButton);

    expect(screen.getByText('Inventory Manager Mock')).toBeInTheDocument();
  });

  test('switches to the Dynamic Pricing view on button click', () => {
    render(<App />);

    const dynamicPricingButton = screen.getByRole('button', { name: 'Dynamic Pricing' });
    fireEvent.click(dynamicPricingButton);

    expect(screen.getByText('Dynamic Pricing Dashboard Mock')).toBeInTheDocument();
  });
});
