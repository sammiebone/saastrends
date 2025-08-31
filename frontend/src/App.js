import React, { useState } from 'react';
import './App.css';
import TrendingTopicsDashboard from './components/TrendingTopicsDashboard';
import ContentIdeaGenerator from './components/ContentIdeaGenerator';

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
        </nav>
      </header>
      <main>
        {activeView === 'dashboard' ? <TrendingTopicsDashboard /> : <ContentIdeaGenerator />}
      </main>
    </div>
  );
}

export default App;
