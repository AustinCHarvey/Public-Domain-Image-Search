import React, { useState } from 'react';

function App() {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [publicOnly, setPublicOnly] = useState(false);

  const searchImages = async () => {
    if (!query.trim()) return;
    setLoading(true);
    try {
      const response = await fetch(`/api/search?q=${encodeURIComponent(query)}&public_only=${publicOnly}`);
      const data = await response.json();
      setResults(data.results || []);
    } catch (err) {
      console.error('Search failed:', err);
      setResults([]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ padding: '2rem' }}>
      <h1>📷 Public Domain Image Search</h1>
      <input
        type="text"
        placeholder="Search for images..."
        value={query}
        onChange={e => setQuery(e.target.value)}
        onKeyDown={e => e.key === 'Enter' && searchImages()}
        style={{ width: '300px', marginRight: '10px' }}
      />
      <label>
        <input
          type="checkbox"
          checked={publicOnly}
          onChange={e => setPublicOnly(e.target.checked)}
        />{' '}
        Only Public Domain
      </label>
      <button onClick={searchImages}>Search</button>

      {loading && <p>Searching...</p>}

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem', marginTop: '2rem' }}>
        {results.map((img, i) => (
          <div key={i}>
            <a href={img.link} target="_blank" rel="noreferrer">
              <img src={img.thumbnail} alt={img.title} style={{ width: '100%' }} />
            </a>
            <p>{img.title}</p>
            <small>{img.source} — {img.license}</small>
          </div>
        ))}
      </div>
    </div>
  );
}

export default App;