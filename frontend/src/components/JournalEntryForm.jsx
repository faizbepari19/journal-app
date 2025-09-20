import { useState, useEffect } from 'react';
import useEntriesStore from '../store/entriesStore';

const JournalEntryForm = ({ selectedEntry, onEntrySaved }) => {
  const [content, setContent] = useState('');
  const [entryDate, setEntryDate] = useState(new Date().toISOString().split('T')[0]); // Today's date in YYYY-MM-DD format
  const { createEntry, updateEntry, isLoading, error } = useEntriesStore();

  // Get today's date for max date validation
  const today = new Date().toISOString().split('T')[0];

  // If editing an existing entry, populate the form
  useEffect(() => {
    if (selectedEntry) {
      setContent(selectedEntry.content);
      // Set the date to the entry's creation date
      const entryCreatedDate = new Date(selectedEntry.entry_date).toISOString().split('T')[0];
      setEntryDate(entryCreatedDate);
    } else {
      setContent('');
      setEntryDate(today);
    }
  }, [selectedEntry, today]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (content.trim()) {
      const entryData = {
        content: content.trim(),
        entry_date: entryDate
      };

      let result;
      if (selectedEntry) {
        result = await updateEntry(selectedEntry.id, entryData);
      } else {
        result = await createEntry(entryData);
      }
      
      if (result.success) {
        setContent('');
        setEntryDate(today);
        if (onEntrySaved) onEntrySaved();
      }
    }
  };

  const handleCancel = () => {
    setContent('');
    setEntryDate(today);
    if (onEntrySaved) onEntrySaved();
  };

  return (
    <div className="space-y-6">
      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Entry Date */}
        <div className="space-y-2">
          <label htmlFor="entry-date" className="block text-sm font-medium text-gray-700 dark:text-gray-300">
            Entry Date
          </label>
          <div className="relative">
            <input
              id="entry-date"
              type="date"
              value={entryDate}
              onChange={(e) => setEntryDate(e.target.value)}
              max={today}
              className="
                w-full px-4 py-3 rounded-xl 
                bg-gray-50 dark:bg-gray-700 
                border border-gray-300 dark:border-gray-600 
                text-gray-900 dark:text-white
                focus:ring-2 focus:ring-primary-500 focus:border-transparent
                disabled:opacity-50 disabled:cursor-not-allowed
                transition-all duration-200
              "
              disabled={isLoading}
              required
            />
            <div className="absolute inset-y-0 right-0 pr-4 flex items-center pointer-events-none">
              <svg className="h-5 w-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
              </svg>
            </div>
          </div>
        </div>

        {/* Entry Content */}
        <div className="space-y-2">
          <label htmlFor="entry-content" className="block text-sm font-medium text-gray-700 dark:text-gray-300">
            What's on your mind?
          </label>
          <div className="relative">
            <textarea
              id="entry-content"
              value={content}
              onChange={(e) => setContent(e.target.value)}
              placeholder={`Write about your ${entryDate === today ? 'day' : 'thoughts'}...`}
              className="
                w-full px-4 py-3 rounded-xl 
                bg-gray-50 dark:bg-gray-700 
                border border-gray-300 dark:border-gray-600 
                text-gray-900 dark:text-white
                placeholder-gray-500 dark:placeholder-gray-400
                focus:ring-2 focus:ring-primary-500 focus:border-transparent
                disabled:opacity-50 disabled:cursor-not-allowed
                transition-all duration-200
                resize-y min-h-[160px]
                text-base leading-relaxed
              "
              disabled={isLoading}
              required
            />
          </div>
          <p className="text-sm text-gray-500 dark:text-gray-400">
            {content.length} characters • Be honest, be yourself
          </p>
        </div>
        
        {/* Form Actions */}
        <div className="flex gap-3 pt-4">
          {selectedEntry && (
            <button
              type="button"
              onClick={handleCancel}
              className="
                px-6 py-3 text-sm font-medium
                text-gray-700 dark:text-gray-300
                bg-white dark:bg-gray-700 
                border border-gray-300 dark:border-gray-600
                rounded-xl hover:bg-gray-50 dark:hover:bg-gray-600
                focus:outline-none focus:ring-2 focus:ring-gray-500 focus:ring-offset-2
                dark:focus:ring-offset-gray-800
                disabled:opacity-50 disabled:cursor-not-allowed
                transition-all duration-200
                min-w-[100px]
              "
              disabled={isLoading}
            >
              Cancel
            </button>
          )}
          <button
            type="submit"
            disabled={isLoading || !content.trim()}
            className="
              flex-1 px-6 py-3 text-sm font-medium text-white
              bg-gradient-to-r from-primary-500 to-accent-500
              hover:from-primary-600 hover:to-accent-600
              rounded-xl focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2
              dark:focus:ring-offset-gray-800
              disabled:opacity-50 disabled:cursor-not-allowed
              transform transition-all duration-200
              hover:scale-[1.02] active:scale-[0.98]
              shadow-lg hover:shadow-xl
              flex items-center justify-center space-x-2
            "
          >
            {isLoading ? (
              <>
                <svg className="animate-spin h-4 w-4 text-white" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                  <path className="opacity-75" fill="currentColor" d="m4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                </svg>
                <span>Saving...</span>
              </>
            ) : (
              <>
                <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                </svg>
                <span>{selectedEntry ? 'Update Entry' : 'Save Entry'}</span>
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

export default JournalEntryForm;
