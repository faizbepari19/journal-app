import { useState } from 'react';
import useSearchStore from '../store/searchStore';

const SearchBar = () => {
  const [query, setQuery] = useState('');
  const { search, isLoading, error } = useSearchStore();

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (query.trim()) {
      await search(query.trim());
    }
  };

  return (
    <div className="search-bar">
      <form onSubmit={handleSubmit} className="search-form">
        <div className="search-input-group">
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Ask anything about your journal entries..."
            className="search-input"
            disabled={isLoading}
          />
          <button
            type="submit"
            disabled={isLoading || !query.trim()}
            className="search-button"
          >
            {isLoading ? 'Searching...' : 'Search'}
          </button>
        </div>
      </form>
      
      {error && (
        <div className="search-error">
          <p>{error}</p>
        </div>
      )}
    </div>
  );
};

export default SearchBar;
