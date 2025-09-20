import useSearchStore from '../store/searchStore';

const SearchResultsDisplay = () => {
  const { searchResult, isLoading, clearSearch } = useSearchStore();

  if (isLoading) {
    return (
      <div className="mt-6 bg-gradient-to-r from-primary-50 to-accent-50 dark:from-gray-700 dark:to-gray-800 rounded-xl border border-primary-200 dark:border-gray-600 p-8">
        <div className="flex flex-col items-center justify-center space-y-4">
          <div className="relative">
            <div className="w-12 h-12 border-4 border-primary-200 dark:border-gray-600 rounded-full animate-spin">
              <div className="absolute top-0 left-0 w-12 h-12 border-4 border-transparent border-t-primary-500 rounded-full animate-spin"></div>
            </div>
          </div>
          <div className="text-center">
            <p className="text-lg font-medium text-gray-900 dark:text-white mb-2">
              Analyzing your journal entries...
            </p>
            <p className="text-sm text-gray-600 dark:text-gray-400">
              This may take a few moments
            </p>
          </div>
        </div>
      </div>
    );
  }

  if (!searchResult) {
    return null;
  }

  return (
    <div className="mt-6 bg-gradient-to-r from-primary-50 to-accent-50 dark:from-gray-700 dark:to-gray-800 rounded-xl border border-primary-200 dark:border-gray-600 animate-fade-in">
      <div className="p-6">
        {/* Header */}
        <div className="flex justify-between items-start mb-6">
          <div className="flex items-center">
            <div className="p-2 bg-gradient-to-r from-primary-500 to-accent-500 rounded-lg mr-4">
              <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
              </svg>
            </div>
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
              AI Insights
            </h3>
          </div>
          
          <button 
            onClick={clearSearch} 
            className="
              p-2 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300
              hover:bg-gray-100 dark:hover:bg-gray-600 rounded-lg
              transition-all duration-200
              focus:outline-none focus:ring-2 focus:ring-primary-500
            "
            title="Clear search results"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
        
        {/* Query */}
        <div className="mb-6 p-4 bg-white/50 dark:bg-gray-800/50 rounded-lg border border-white/20 dark:border-gray-700/50">
          <div className="flex items-start space-x-3">
            <div className="flex-shrink-0 mt-1">
              <svg className="w-4 h-4 text-primary-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <div className="flex-1">
              <p className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Your question:</p>
              <p className="text-gray-900 dark:text-white font-medium italic">"{searchResult.query}"</p>
            </div>
          </div>
        </div>
        
        {/* Response */}
        <div className="mb-4">
          <div className="flex items-start space-x-3">
            <div className="flex-shrink-0 mt-1">
              <svg className="w-4 h-4 text-accent-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
              </svg>
            </div>
            <div className="flex-1">
              <p className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">AI Response:</p>
              <div className="prose prose-gray dark:prose-invert max-w-none">
                <div className="text-gray-900 dark:text-white leading-relaxed whitespace-pre-wrap">
                  {searchResult.response}
                </div>
              </div>
            </div>
          </div>
        </div>
        
        {/* Meta */}
        <div className="pt-4 border-t border-white/20 dark:border-gray-700/50">
          <div className="flex items-center text-sm text-gray-600 dark:text-gray-400">
            <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <span>
              Based on {searchResult.relevantEntriesCount} relevant journal 
              {searchResult.relevantEntriesCount === 1 ? ' entry' : ' entries'}
            </span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SearchResultsDisplay;
