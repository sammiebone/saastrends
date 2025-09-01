import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import Scheduler from './Scheduler';

// Mock the global fetch function
global.fetch = jest.fn();

// Mock the react-big-calendar component
jest.mock('react-big-calendar', () => ({
  Calendar: ({ events }) => (
    <div data-testid="calendar">
      {events.map(e => (
        <div key={e.id}>{e.title}</div>
      ))}
    </div>
  ),
  momentLocalizer: () => {},
}));

describe('Scheduler', () => {
  beforeEach(() => {
    fetch.mockClear();
    // Mock the initial fetch for posts, return empty array
    fetch.mockResolvedValue({
      ok: true,
      json: async () => [],
    });
  });

  test('renders the component', async () => {
    render(<Scheduler />);
    expect(screen.getByText('Blog Post Scheduler')).toBeInTheDocument();
    expect(screen.getByTestId('calendar')).toBeInTheDocument();
  });

  test('can create a new draft post', async () => {
    render(<Scheduler />);

    // Mock the POST request for creating a draft
    fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ id: 1, title: 'New Draft', topic: 'drafts' }),
    });

    // Mock the window.alert function
    const alertMock = jest.spyOn(window, 'alert').mockImplementation(() => {});

    fireEvent.change(screen.getByPlaceholderText('Post Title'), { target: { value: 'New Draft' } });
    fireEvent.change(screen.getByPlaceholderText('Main Topic/Keyword'), { target: { value: 'drafts' } });
    fireEvent.click(screen.getByRole('button', { name: 'Save as Draft' }));

    await waitFor(() => {
      expect(fetch).toHaveBeenCalledWith('/api/posts', expect.any(Object));
    });

    expect(alertMock).toHaveBeenCalledWith('Draft created! It will not appear on the calendar until scheduled.');
    alertMock.mockRestore();
  });

  test('can get a publishing recommendation', async () => {
    render(<Scheduler />);

    // Mock the recommendation API call
    fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ day: 'Tuesday', hour: 15 }),
    });

    fireEvent.change(screen.getByPlaceholderText('Main Topic/Keyword'), { target: { value: 'new topic' } });
    fireEvent.click(screen.getByRole('button', { name: 'Get Recommendation' }));

    await waitFor(() => {
      expect(fetch).toHaveBeenCalledWith('/api/recommendations?topic=new%20topic');
    });

    expect(screen.getByText('Recommended time: Tuesday at 15:00')).toBeInTheDocument();
  });
});
