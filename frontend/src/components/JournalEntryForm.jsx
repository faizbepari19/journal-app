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
    <div className="journal-entry-form">
      <h2>{selectedEntry ? 'Edit Entry' : 'Write a New Entry'}</h2>
      
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label htmlFor="entry-date" className="form-label">
            Entry Date
          </label>
          <input
            id="entry-date"
            type="date"
            value={entryDate}
            onChange={(e) => setEntryDate(e.target.value)}
            max={today}
            className="date-picker"
            disabled={isLoading}
            required
          />
        </div>

        <div className="form-group">
          <label htmlFor="entry-content" className="form-label">
            What's on your mind?
          </label>
          <textarea
            id="entry-content"
            value={content}
            onChange={(e) => setContent(e.target.value)}
            placeholder={`Write about your ${entryDate === today ? 'day' : 'thoughts'}...`}
            className="entry-textarea"
            rows="6"
            disabled={isLoading}
            required
          />
        </div>
        
        <div className="form-actions">
          {selectedEntry && (
            <button
              type="button"
              onClick={handleCancel}
              className="cancel-button"
              disabled={isLoading}
            >
              Cancel
            </button>
          )}
          <button
            type="submit"
            disabled={isLoading || !content.trim()}
            className="submit-button"
          >
            {isLoading ? 'Saving...' : selectedEntry ? 'Update Entry' : 'Save Entry'}
          </button>
        </div>
      </form>
      
      {error && (
        <div className="form-error">
          <p>{error}</p>
        </div>
      )}
    </div>
  );
};

export default JournalEntryForm;
