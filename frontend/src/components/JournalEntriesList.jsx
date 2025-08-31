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

  const truncateContent = (content, maxLength = 60) => {
    return content.length > maxLength ? content.substring(0, maxLength) + '...' : content;
  };

  if (isLoading && entries.length === 0) {
    return (
      <div className={`entries-loading ${isNavigation ? 'nav-style' : ''}`}>
        <p>Loading entries...</p>
      </div>
    );
  }

  if (entries.length === 0) {
    return (
      <div className={`entries-empty ${isNavigation ? 'nav-style' : ''}`}>
        <p>No entries yet</p>
        {!isNavigation && <p>Start by writing your first journal entry above!</p>}
      </div>
    );
  }

  if (isNavigation) {
    // Navigation sidebar style
    return (
      <div className="journal-entries-nav">
        {error && (
          <div className="entries-error">
            <p>{error}</p>
          </div>
        )}
        
        <div className="entries-nav-list">
          {entries.map((entry) => (
            <div 
              key={entry.id} 
              className={`entry-nav-item ${selectedEntryId === entry.id ? 'selected' : ''}`}
              onClick={() => handleEntryClick(entry)}
            >
              <div className="entry-nav-header">
                <div className="entry-nav-date">
                  <div className="date-text">{formatDate(entry.entry_date)}</div>
                  <div className="time-text">{formatTime(entry.entry_date)}</div>
                </div>
                <button
                  onClick={(e) => handleDelete(entry.id, e)}
                  className="entry-nav-delete"
                  title="Delete entry"
                >
                  ✕
                </button>
              </div>
              <div className="entry-nav-preview">
                {truncateContent(entry.content)}
              </div>
            </div>
          ))}
        </div>
      </div>
    );
  }

  // Regular full view style (fallback)
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
            <div 
              className="entry-header clickable"
              onClick={() => toggleEntryExpansion(entry.id)}
            >
              <div className="entry-date">
                {formatDate(entry.created_at)} at {formatTime(entry.created_at)}
              </div>
              <div className="entry-toggle">
                {expandedEntries.has(entry.id) ? '▼' : '▶'}
              </div>
            </div>
            
            {expandedEntries.has(entry.id) && (
              <div className="entry-content">
                <p className="entry-text">{entry.content}</p>
                <div className="entry-actions">
                  <button
                    onClick={() => handleEntryClick(entry)}
                    className="edit-button"
                  >
                    Edit
                  </button>
                  <button
                    onClick={(e) => handleDelete(entry.id, e)}
                    className="delete-button"
                  >
                    Delete
                  </button>
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
