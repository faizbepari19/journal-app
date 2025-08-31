import { useState } from 'react';
import useEntriesStore from '../store/entriesStore';

const JournalEntryForm = () => {
  const [content, setContent] = useState('');
  const { createEntry, isLoading, error } = useEntriesStore();

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (content.trim()) {
      const result = await createEntry(content.trim());
      if (result.success) {
        setContent('');
      }
    }
  };

  return (
    <div className="journal-entry-form">
      <h2>Write a New Entry</h2>
      
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <textarea
            value={content}
            onChange={(e) => setContent(e.target.value)}
            placeholder="What's on your mind today?"
            className="entry-textarea"
            rows="6"
            disabled={isLoading}
            required
          />
        </div>
        
        <div className="form-actions">
          <button
            type="submit"
            disabled={isLoading || !content.trim()}
            className="submit-button"
          >
            {isLoading ? 'Saving...' : 'Save Entry'}
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
