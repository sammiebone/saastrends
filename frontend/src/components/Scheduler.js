import React, { useState, useEffect } from 'react';
import { Calendar, momentLocalizer } from 'react-big-calendar';
import moment from 'moment';
import 'react-big-calendar/lib/css/react-big-calendar.css';

const localizer = momentLocalizer(moment);

function Scheduler() {
  const [events, setEvents] = useState([]);
  const [title, setTitle] = useState('');
  const [topic, setTopic] = useState('');
  const [recommendation, setRecommendation] = useState(null);
  const [error, setError] = useState('');

  // Fetch posts on mount
  useEffect(() => {
    const fetchPosts = async () => {
      try {
        const response = await fetch('/api/posts');
        const posts = await response.json();
        const calendarEvents = posts.map(post => ({
          id: post.id,
          title: post.title,
          start: new Date(post.scheduled_time),
          end: moment(post.scheduled_time).add(1, 'hour').toDate(),
          resource: post,
        }));
        setEvents(calendarEvents);
      } catch (e) {
        setError('Failed to load posts.');
      }
    };
    fetchPosts();
  }, []);

  const handleGetRecommendation = async () => {
    if (!topic) {
      setError('Please enter a topic to get a recommendation.');
      return;
    }
    setError('');
    setRecommendation(null);
    try {
      const response = await fetch(`/api/recommendations?topic=${encodeURIComponent(topic)}`);
      if (response.ok) {
        const rec = await response.json();
        setRecommendation(`Recommended time: ${rec.day} at ${rec.hour}:00`);
      } else {
        const err = await response.json();
        setError(err.error || 'Could not get recommendation.');
      }
    } catch (e) {
      setError('Failed to get recommendation.');
    }
  };

  const handleCreateDraft = async (e) => {
      e.preventDefault();
      if (!title || !topic) {
          setError('Title and topic are required to create a draft.');
          return;
      }
      try {
          const response = await fetch('/api/posts', {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({ title, topic, content: '' }),
          });
          if (response.ok) {
              // For simplicity, we just alert and would refetch events in a real app
              alert('Draft created! It will not appear on the calendar until scheduled.');
              setTitle('');
              setTopic('');
          } else {
              const err = await response.json();
              setError(err.error || 'Failed to create draft.');
          }
      } catch (e) {
          setError('Failed to create draft.');
      }
  };

  // In a full app, selecting an event on the calendar would open a modal
  // to edit and schedule it. For now, we'll keep it simple.

  return (
    <div className="feature-container">
      <h2>Blog Post Scheduler</h2>
      <div className="scheduler-form">
        <h3>Create New Post Draft</h3>
        <form onSubmit={handleCreateDraft}>
          <input
            type="text"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            placeholder="Post Title"
          />
          <input
            type="text"
            value={topic}
            onChange={(e) => setTopic(e.target.value)}
            placeholder="Main Topic/Keyword"
          />
          <button type="button" onClick={handleGetRecommendation}>Get Recommendation</button>
          <button type="submit">Save as Draft</button>
        </form>
        {recommendation && <p className="recommendation">{recommendation}</p>}
        {error && <p className="error">{error}</p>}
      </div>

      <div className="calendar-container">
        <h3>Content Calendar</h3>
        <Calendar
          localizer={localizer}
          events={events}
          startAccessor="start"
          endAccessor="end"
          style={{ height: 600 }}
        />
      </div>
    </div>
  );
}

export default Scheduler;
