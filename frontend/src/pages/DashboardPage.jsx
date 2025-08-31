import { useEffect } from 'react';
import useAuthStore from '../store/authStore';
import SearchBar from '../components/SearchBar';
import SearchResultsDisplay from '../components/SearchResultsDisplay';
import JournalEntryForm from '../components/JournalEntryForm';
import JournalEntriesList from '../components/JournalEntriesList';

const DashboardPage = () => {
  const { user, logout } = useAuthStore();

  const handleLogout = () => {
    logout();
  };

  return (
    <div className="dashboard">
      <header className="dashboard-header">
        <div className="header-content">
          <h1>My Journal</h1>
          <div className="header-user">
            <span>Welcome, {user?.username}</span>
            <button onClick={handleLogout} className="logout-button">
              Logout
            </button>
          </div>
        </div>
      </header>

      <main className="dashboard-main">
        <div className="dashboard-content">
          {/* AI Search Section */}
          <section className="search-section">
            <div className="section-header">
              <h2>Ask About Your Entries</h2>
              <p>Ask questions about your past journal entries and get AI-powered insights</p>
            </div>
            <SearchBar />
            <SearchResultsDisplay />
          </section>

          {/* New Entry Section */}
          <section className="new-entry-section">
            <JournalEntryForm />
          </section>

          {/* Entries List Section */}
          <section className="entries-section">
            <JournalEntriesList />
          </section>
        </div>
      </main>
    </div>
  );
};

export default DashboardPage;
