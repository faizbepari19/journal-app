import { useEffect, useState } from 'react';
import useAuthStore from '../store/authStore';
import ThemeToggle from '../components/ThemeToggle';
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
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      {/* Header */}
      <header className="sticky top-0 z-50 bg-white/80 dark:bg-gray-900/80 backdrop-blur-md border-b border-gray-200 dark:border-gray-700">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            {/* Left side */}
            <div className="flex items-center space-x-4">
              <button 
                onClick={toggleSidebar} 
                className="
                  p-2 rounded-lg text-gray-600 dark:text-gray-400 
                  hover:bg-gray-100 dark:hover:bg-gray-800 
                  focus:outline-none focus:ring-2 focus:ring-primary-500
                  transition-all duration-200
                "
                aria-label="Toggle sidebar"
              >
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
                </svg>
              </button>
              
              <div className="flex items-center space-x-3">
                <div className="p-2 bg-gradient-to-r from-primary-500 to-accent-500 rounded-lg">
                  <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.746 0 3.332.477 4.5 1.253v13C19.832 18.477 18.246 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
                  </svg>
                </div>
                <h1 className="text-2xl font-bold text-gray-900 dark:text-white">My Journal</h1>
              </div>
            </div>

            {/* Right side */}
            <div className="flex items-center space-x-4">
              <div className="hidden sm:flex items-center text-sm text-gray-600 dark:text-gray-400">
                <span>Welcome back,</span>
                <span className="ml-1 font-semibold text-gray-900 dark:text-white">
                  {user?.username}
                </span>
              </div>
              
              <ThemeToggle />
              
              <button 
                onClick={handleLogout} 
                className="
                  px-4 py-2 text-sm font-medium text-gray-700 dark:text-gray-300
                  bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600
                  rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700
                  focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2
                  dark:focus:ring-offset-gray-900
                  transition-all duration-200
                "
              >
                Sign out
              </button>
            </div>
          </div>
        </div>
      </header>

      <div className="flex max-w-7xl mx-auto">
        {/* Sidebar */}
        <aside className={`
          ${isSidebarCollapsed ? 'w-0 overflow-hidden' : 'w-80'}
          bg-white dark:bg-gray-800 border-r border-gray-200 dark:border-gray-700
          h-[calc(100vh-4rem)] sticky top-16
          transition-all duration-300 ease-in-out
          flex-shrink-0 flex flex-col
        `}>
          <div className="p-6 border-b border-gray-200 dark:border-gray-700 flex-shrink-0">
            <h2 className="text-lg font-semibold text-gray-900 dark:text-white flex items-center">
              <svg className="w-5 h-5 mr-2 text-primary-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
              </svg>
              Your Entries
            </h2>
            <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
              Click any entry to edit
            </p>
          </div>
          
          <div className="flex-1 overflow-y-auto min-h-0 scrollbar-thin mobile-scroll">
            <JournalEntriesList 
              isNavigation={true}
              onEntrySelect={setSelectedEntry}
              selectedEntryId={selectedEntry?.id}
            />
          </div>
        </aside>

        {/* Main content */}
        <main className="flex-1 p-6 space-y-8 overflow-y-auto max-h-[calc(100vh-4rem)]">
          {/* AI Search Section */}
          <section className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-8">
            <div className="mb-6">
              <div className="flex items-center mb-4">
                <div className="p-2 bg-gradient-to-r from-primary-500 to-accent-500 rounded-lg mr-4">
                  <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                  </svg>
                </div>
                <div>
                  <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
                    Ask About Your Entries
                  </h2>
                  <p className="text-gray-600 dark:text-gray-400 mt-1">
                    Get AI-powered insights from your past journal entries
                  </p>
                </div>
              </div>
            </div>
            
            <SearchBar />
            <SearchResultsDisplay />
          </section>

          {/* New Entry Section */}
          <section className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-8">
            <div className="flex items-center mb-6">
              <div className="p-2 bg-gradient-to-r from-accent-500 to-primary-500 rounded-lg mr-4">
                <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z" />
                </svg>
              </div>
              <div>
                <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
                  {selectedEntry ? 'Edit Entry' : 'Write New Entry'}
                </h2>
                <p className="text-gray-600 dark:text-gray-400 mt-1">
                  {selectedEntry ? 'Make changes to your existing entry' : 'Capture your thoughts and experiences'}
                </p>
              </div>
            </div>
            
            <JournalEntryForm 
              selectedEntry={selectedEntry} 
              onEntrySaved={() => setSelectedEntry(null)} 
            />
          </section>
        </main>
      </div>
    </div>
  );
};

export default DashboardPage;
