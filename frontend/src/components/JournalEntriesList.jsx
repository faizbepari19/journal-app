import { useState, useEffect } from 'react';
import { format, parseISO } from 'date-fns';
import useEntriesStore from '../store/entriesStore';

const JournalEntriesList = () => {
  const { entries, fetchEntries, updateEntry, deleteEntry, isLoading, error } = useEntriesStore();
  const [editingId, setEditingId] = useState(null);
  const [editContent, setEditContent] = useState('');

  useEffect(() => {
    fetchEntries();
  }, [fetchEntries]);

  const handleStartEdit = (entry) => {
    setEditingId(entry.id);
    setEditContent(entry.content);
  };

  const handleSaveEdit = async () => {
    if (editContent.trim()) {
      const result = await updateEntry(editingId, editContent.trim());
      if (result.success) {
        setEditingId(null);
        setEditContent('');
      }
    }
  };

  const handleCancelEdit = () => {
    setEditingId(null);
    setEditContent('');
  };

  const handleDelete = async (entryId) => {
    if (window.confirm('Are you sure you want to delete this entry?')) {
      await deleteEntry(entryId);
    }
  };

  const formatDate = (dateString) => {
    try {
      return format(parseISO(dateString), 'PPP p');
    } catch {
      return dateString;
    }
  };

  if (isLoading && entries.length === 0) {
    return (
      <div className="entries-loading">
        <p>Loading your journal entries...</p>
      </div>
    );
  }

  if (entries.length === 0) {
    return (
      <div className="entries-empty">
        <h3>No entries yet</h3>
        <p>Start by writing your first journal entry above!</p>
      </div>
    );
  }

  return (
    <div className="journal-entries-list">
      <h2>Your Journal Entries</h2>
      
      {error && (
        <div className="entries-error">
          <p>{error}</p>
        </div>
      )}
      
      <div className="entries-container">
        {entries.map((entry) => (
          <div key={entry.id} className="journal-entry">
            <div className="entry-header">
              <div className="entry-date">
                {formatDate(entry.created_at)}
              </div>
              <div className="entry-actions">
                {editingId !== entry.id && (
                  <>
                    <button
                      onClick={() => handleStartEdit(entry)}
                      className="edit-button"
                    >
                      Edit
                    </button>
                    <button
                      onClick={() => handleDelete(entry.id)}
                      className="delete-button"
                    >
                      Delete
                    </button>
                  </>
                )}
              </div>
            </div>
            
            <div className="entry-content">
              {editingId === entry.id ? (
                <div className="entry-edit-form">
                  <textarea
                    value={editContent}
                    onChange={(e) => setEditContent(e.target.value)}
                    className="edit-textarea"
                    rows="4"
                  />
                  <div className="edit-actions">
                    <button
                      onClick={handleSaveEdit}
                      className="save-button"
                      disabled={!editContent.trim()}
                    >
                      Save
                    </button>
                    <button
                      onClick={handleCancelEdit}
                      className="cancel-button"
                    >
                      Cancel
                    </button>
                  </div>
                </div>
              ) : (
                <p className="entry-text">{entry.content}</p>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default JournalEntriesList;
