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
    <div className="space-y-4">
      <form onSubmit={handleSubmit} className="space-y-4">
        <div className="flex gap-3">
          <div className="flex-1 relative">
            <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
              <svg className="h-5 w-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
            </div>
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Ask anything about your journal entries..."
              className="
                w-full pl-12 pr-4 py-3 
                bg-gray-50 dark:bg-gray-700 
                border border-gray-300 dark:border-gray-600 
                rounded-xl text-gray-900 dark:text-white 
                placeholder-gray-500 dark:placeholder-gray-400
                focus:ring-2 focus:ring-primary-500 focus:border-transparent
                disabled:opacity-50 disabled:cursor-not-allowed
                transition-all duration-200
                text-base
              "
              disabled={isLoading}
            />
          </div>
          <button
            type="submit"
            disabled={isLoading || !query.trim()}
            className="
              px-6 py-3 bg-gradient-to-r from-primary-500 to-accent-500
              text-white font-semibold rounded-xl
              hover:from-primary-600 hover:to-accent-600
              focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2
              dark:focus:ring-offset-gray-800
              disabled:opacity-50 disabled:cursor-not-allowed
              transform transition-all duration-200
              hover:scale-105 active:scale-95
              shadow-lg hover:shadow-xl
              flex items-center space-x-2
              min-w-[120px]
            "
          >
            {isLoading ? (
              <>
                <svg className="animate-spin h-4 w-4 text-white" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                  <path className="opacity-75" fill="currentColor" d="m4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                </svg>
                <span>Searching...</span>
              </>
            ) : (
              <>
                <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                </svg>
                <span>Search</span>
              </>
            )}
          </button>
        </div>
      </form>
      
      {error && (
        <div className="p-4 rounded-xl bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 animate-slide-in">
          <div className="flex items-center">
            <svg className="w-5 h-5 text-red-500 mr-3 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
            </svg>
            <p className="text-sm font-medium text-red-700 dark:text-red-400">{error}</p>
          </div>
        </div>
      )}
    </div>
  );
};

export default SearchBar;
