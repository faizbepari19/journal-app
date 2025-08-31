import useSearchStore from '../store/searchStore';

const SearchResultsDisplay = () => {
  const { searchResult, isLoading, clearSearch } = useSearchStore();

  if (isLoading) {
    return (
      <div className="search-results loading">
        <div className="loading-spinner"></div>
        <p>Analyzing your journal entries...</p>
      </div>
    );
  }

  if (!searchResult) {
    return null;
  }

  return (
    <div className="search-results">
      <div className="search-results-header">
        <h3>Search Results</h3>
        <button onClick={clearSearch} className="close-button">
          ×
        </button>
      </div>
      
      <div className="search-query">
        <strong>Your question:</strong> {searchResult.query}
      </div>
      
      <div className="search-response">
        <div className="response-content">
          {searchResult.response}
        </div>
        
        <div className="response-meta">
          <small>
            Based on {searchResult.relevantEntriesCount} relevant journal entries
          </small>
        </div>
      </div>
    </div>
  );
};

export default SearchResultsDisplay;
