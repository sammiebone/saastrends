import React, { useState } from 'react';
import './App.css';
import TrendingTopicsDashboard from './components/TrendingTopicsDashboard';
import ContentIdeaGenerator from './components/ContentIdeaGenerator';
import KeywordTracker from './components/KeywordTracker';
import SeoDashboard from './components/SeoDashboard';

function App() {
  const [activeView, setActiveView] = useState('dashboard'); // 'dashboard' or 'generator'

  return (
    <div className="App">
      <header className="App-header">
        <h1>Google Trends SaaS</h1>
        <nav>
          <button onClick={() => setActiveView('dashboard')} disabled={activeView === 'dashboard'}>
            Trending Dashboard
          </button>
          <button onClick={() => setActiveView('generator')} disabled={activeView === 'generator'}>
            Content Idea Generator
          </button>
          <button onClick={() => setActiveView('tracker')} disabled={activeView === 'tracker'}>
            Keyword Tracker
          </button>
          <button onClick={() => setActiveView('seoDashboard')} disabled={activeView === 'seoDashboard'}>
            SEO Dashboard
          </button>
        </nav>
      </header>
      <main>
        {activeView === 'dashboard' && <TrendingTopicsDashboard />}
        {activeView === 'generator' && <ContentIdeaGenerator />}
        {activeView === 'tracker' && <KeywordTracker />}
        {activeView === 'seoDashboard' && <SeoDashboard />}
      </main>
    </div>
  );
}

export default App;
