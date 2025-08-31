import { useEffect, useState } from 'react';
import useAuthStore from '../store/authStore';
import SearchBar from '../components/SearchBar';
import SearchResultsDisplay from '../components/SearchResultsDisplay';
import JournalEntryForm from '../components/JournalEntryForm';
import JournalEntriesList from '../components/JournalEntriesList';

const DashboardPage = () => {
  const { user, logout } = useAuthStore();
  const [isSidebarCollapsed, setIsSidebarCollapsed] = useState(false);
  const [selectedEntry, setSelectedEntry] = useState(null);

  const handleLogout = () => {
    logout();
  };

  const toggleSidebar = () => {
    setIsSidebarCollapsed(!isSidebarCollapsed);
  };

  return (
    <div className="dashboard">
      <header className="dashboard-header">
        <div className="header-content">
          <div className="header-left">
            <button 
              onClick={toggleSidebar} 
              className="sidebar-toggle"
              aria-label="Toggle sidebar"
            >
              ☰
            </button>
            <h1>My Journal</h1>
          </div>
          <div className="header-user">
            <span>Welcome, {user?.username}</span>
            <button onClick={handleLogout} className="logout-button">
              Logout
            </button>
          </div>
        </div>
      </header>

      <div className="dashboard-body">
        {/* Sidebar with entries navigation */}
        <aside className={`dashboard-sidebar ${isSidebarCollapsed ? 'collapsed' : ''}`}>
          <div className="sidebar-header">
            <h3>Journal Entries</h3>
          </div>
          <JournalEntriesList 
            isNavigation={true}
            onEntrySelect={setSelectedEntry}
            selectedEntryId={selectedEntry?.id}
          />
        </aside>

        {/* Main content area */}
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
              <JournalEntryForm selectedEntry={selectedEntry} onEntrySaved={() => setSelectedEntry(null)} />
            </section>
          </div>
        </main>
      </div>
    </div>
  );
};

export default DashboardPage;
