import { useState, useEffect } from 'react';
import { format, parseISO } from 'date-fns';
import useEntriesStore from '../store/entriesStore';

const JournalEntriesList = ({ isNavigation = false, onEntrySelect, selectedEntryId }) => {
  const { entries, fetchEntries, deleteEntry, isLoading, error } = useEntriesStore();
  const [expandedEntries, setExpandedEntries] = useState(new Set());

  useEffect(() => {
    fetchEntries();
  }, [fetchEntries]);

  const toggleEntryExpansion = (entryId) => {
    const newExpanded = new Set(expandedEntries);
    if (newExpanded.has(entryId)) {
      newExpanded.delete(entryId);
    } else {
      newExpanded.add(entryId);
    }
    setExpandedEntries(newExpanded);
  };

  const handleEntryClick = (entry) => {
    if (isNavigation && onEntrySelect) {
      onEntrySelect(entry);
    } else {
      toggleEntryExpansion(entry.id);
    }
  };

  const handleDelete = async (entryId, e) => {
    e.stopPropagation(); // Prevent triggering entry click
    if (window.confirm('Are you sure you want to delete this entry?')) {
      await deleteEntry(entryId);
      // If the deleted entry was selected, clear selection
      if (selectedEntryId === entryId && onEntrySelect) {
        onEntrySelect(null);
      }
    }
  };

  const formatDate = (dateString) => {
    try {
      return format(parseISO(dateString), 'MMM dd, yyyy');
    } catch {
      return dateString;
    }
  };

  const formatTime = (dateString) => {
    try {
      return format(parseISO(dateString), 'h:mm a');
    } catch {
      return '';
    }
  };

  const formatISTTime = (istString) => {
    // If we have the pre-formatted IST string from backend, use it
    if (istString && istString.includes('IST')) {
      return istString;
    }
    // Fallback to regular formatting
    return istString || '';
  };

  const truncateContent = (content, maxLength = 80) => {
    return content.length > maxLength ? content.substring(0, maxLength) + '...' : content;
  };

  if (isLoading && entries.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center p-8 space-y-4">
        <div className="w-8 h-8 border-4 border-primary-200 dark:border-gray-600 rounded-full animate-spin">
          <div className="absolute w-8 h-8 border-4 border-transparent border-t-primary-500 rounded-full animate-spin"></div>
        </div>
        <p className="text-gray-600 dark:text-gray-400 text-sm">Loading entries...</p>
      </div>
    );
  }

  if (entries.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center p-8 text-center space-y-4">
        <div className="p-4 bg-gray-100 dark:bg-gray-700 rounded-full">
          <svg className="w-8 h-8 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.746 0 3.332.477 4.5 1.253v13C19.832 18.477 18.246 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
          </svg>
        </div>
        <div>
          <p className="text-gray-600 dark:text-gray-400 font-medium">No entries yet</p>
          {!isNavigation && (
            <p className="text-sm text-gray-500 dark:text-gray-500 mt-1">
              Start by writing your first journal entry!
            </p>
          )}
        </div>
      </div>
    );
  }

  if (isNavigation) {
    // Navigation sidebar style
    return (
      <div className="h-full">
        {error && (
          <div className="p-4 m-4 rounded-lg bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800">
            <p className="text-sm text-red-700 dark:text-red-400">{error}</p>
          </div>
        )}
        
        <div className="space-y-1 p-2">
          {entries.map((entry) => (
            <div 
              key={entry.id} 
              className={`
                group relative p-4 rounded-lg cursor-pointer transition-all duration-200
                ${selectedEntryId === entry.id 
                  ? 'bg-gradient-to-r from-primary-50 to-accent-50 dark:from-primary-900/20 dark:to-accent-900/20 border-l-4 border-primary-500' 
                  : 'hover:bg-gray-50 dark:hover:bg-gray-700/50'
                }
              `}
              onClick={() => handleEntryClick(entry)}
            >
              <div className="flex justify-between items-start mb-2">
                <div className="flex-1 min-w-0">
                  <div className="text-sm font-medium text-gray-900 dark:text-white">
                    {formatDate(entry.entry_date || entry.created_at)}
                  </div>
                  <div className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                    {entry.updated_at_ist ? `Updated: ${formatISTTime(entry.updated_at_ist)}` : 
                     entry.created_at_ist ? `Created: ${formatISTTime(entry.created_at_ist)}` : 
                     formatTime(entry.created_at)}
                  </div>
                </div>
                <button
                  onClick={(e) => handleDelete(entry.id, e)}
                  className="
                    opacity-0 group-hover:opacity-100 p-1 rounded text-gray-400 hover:text-red-500 
                    hover:bg-red-50 dark:hover:bg-red-900/20 transition-all duration-200
                    focus:opacity-100 focus:outline-none focus:ring-2 focus:ring-red-500 focus:ring-offset-1
                  "
                  title="Delete entry"
                >
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                  </svg>
                </button>
              </div>
              
              <div className="text-sm text-gray-600 dark:text-gray-400 leading-relaxed line-clamp-2">
                {truncateContent(entry.content)}
              </div>
              
              {selectedEntryId === entry.id && (
                <div className="absolute inset-y-0 left-0 w-1 bg-gradient-to-b from-primary-500 to-accent-500 rounded-r-full"></div>
              )}
            </div>
          ))}
        </div>
      </div>
    );
  }

  // Regular full view style (fallback)
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold text-gray-900 dark:text-white">Your Journal Entries</h2>
        <div className="text-sm text-gray-500 dark:text-gray-400">
          {entries.length} {entries.length === 1 ? 'entry' : 'entries'}
        </div>
      </div>
      
      {error && (
        <div className="p-4 rounded-xl bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800">
          <p className="text-sm font-medium text-red-700 dark:text-red-400">{error}</p>
        </div>
      )}
      
      <div className="space-y-4">
        {entries.map((entry) => (
          <div key={entry.id} className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 overflow-hidden shadow-sm hover:shadow-md transition-shadow duration-200">
            <div 
              className="p-6 cursor-pointer hover:bg-gray-50 dark:hover:bg-gray-700/50 transition-colors duration-200"
              onClick={() => toggleEntryExpansion(entry.id)}
            >
              <div className="flex justify-between items-start">
                <div className="flex-1">
                  <div className="flex items-center space-x-4 mb-2">
                    <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                      {formatDate(entry.entry_date || entry.created_at)}
                    </h3>
                    <div className="text-sm text-gray-500 dark:text-gray-400">
                      {entry.updated_at_ist && (
                        <span>Last updated: {formatISTTime(entry.updated_at_ist)}</span>
                      )}
                      {entry.created_at_ist && !entry.updated_at_ist && (
                        <span>Created: {formatISTTime(entry.created_at_ist)}</span>
                      )}
                    </div>
                  </div>
                  
                  {!expandedEntries.has(entry.id) && (
                    <p className="text-gray-600 dark:text-gray-400 line-clamp-2 leading-relaxed">
                      {entry.content}
                    </p>
                  )}
                </div>
                
                <div className="flex items-center space-x-2 ml-4">
                  <button className="p-2 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 transition-colors duration-200">
                    <svg 
                      className={`w-5 h-5 transform transition-transform duration-200 ${expandedEntries.has(entry.id) ? 'rotate-180' : ''}`}
                      fill="none" 
                      stroke="currentColor" 
                      viewBox="0 0 24 24"
                    >
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                    </svg>
                  </button>
                </div>
              </div>
            </div>
            
            {expandedEntries.has(entry.id) && (
              <div className="px-6 pb-6 border-t border-gray-200 dark:border-gray-700 animate-slide-in">
                <div className="pt-4">
                  <div className="prose prose-gray dark:prose-invert max-w-none">
                    <p className="text-gray-900 dark:text-white leading-relaxed whitespace-pre-wrap">
                      {entry.content}
                    </p>
                  </div>
                  
                  <div className="flex items-center justify-between mt-6 pt-4 border-t border-gray-200 dark:border-gray-700">
                    <div className="text-xs text-gray-500 dark:text-gray-400">
                      {entry.content.length} characters
                    </div>
                    
                    <div className="flex space-x-2">
                      <button
                        onClick={() => handleEntryClick(entry)}
                        className="
                          px-4 py-2 text-sm font-medium text-primary-700 dark:text-primary-400
                          bg-primary-50 dark:bg-primary-900/20 hover:bg-primary-100 dark:hover:bg-primary-900/40
                          rounded-lg transition-colors duration-200
                          focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2
                          dark:focus:ring-offset-gray-800
                        "
                      >
                        Edit
                      </button>
                      <button
                        onClick={(e) => handleDelete(entry.id, e)}
                        className="
                          px-4 py-2 text-sm font-medium text-red-700 dark:text-red-400
                          bg-red-50 dark:bg-red-900/20 hover:bg-red-100 dark:hover:bg-red-900/40
                          rounded-lg transition-colors duration-200
                          focus:outline-none focus:ring-2 focus:ring-red-500 focus:ring-offset-2
                          dark:focus:ring-offset-gray-800
                        "
                      >
                        Delete
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
};

export default JournalEntriesList;
