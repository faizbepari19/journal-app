import { useState, useEffect } from 'react';
import { Link, Navigate } from 'react-router-dom';
import useAuthStore from '../store/authStore';
import ThemeToggle from '../components/ThemeToggle';

const LoginPage = () => {
  const [formData, setFormData] = useState({
    email: '',
    password: '',
  });

  const { login, isLoading, error, isAuthenticated, clearError } = useAuthStore();

  useEffect(() => {
    clearError();
  }, [clearError]);

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    await login(formData);
  };

  if (isAuthenticated) {
    return <Navigate to="/dashboard" replace />;
  }

  return (
    <div className="min-h-screen flex">
      {/* Left side - Login Form */}
      <div className="flex-1 flex items-center justify-center px-4 sm:px-6 lg:px-20 xl:px-24 bg-white dark:bg-gray-900">
        <div className="w-full max-w-md space-y-8 animate-fade-in">
          {/* Header */}
          <div className="text-center">
            <div className="flex justify-center mb-6">
              <div className="p-3 rounded-full bg-gradient-to-r from-primary-500 to-accent-500">
                <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.746 0 3.332.477 4.5 1.253v13C19.832 18.477 18.246 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
                </svg>
              </div>
            </div>
            <h1 className="text-4xl font-bold text-gray-900 dark:text-white mb-3">
              Welcome back
            </h1>
            <p className="text-lg text-gray-600 dark:text-gray-400">
              Sign in to continue your journal journey
            </p>
          </div>

          {/* Form */}
          <form onSubmit={handleSubmit} className="space-y-6">
            <div className="space-y-5">
              <div>
                <label htmlFor="email" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Email address
                </label>
                <input
                  type="email"
                  id="email"
                  name="email"
                  value={formData.email}
                  onChange={handleChange}
                  required
                  disabled={isLoading}
                  className="
                    w-full px-4 py-3 rounded-xl border border-gray-300 dark:border-gray-600
                    bg-white dark:bg-gray-800 text-gray-900 dark:text-white
                    placeholder-gray-500 dark:placeholder-gray-400
                    focus:ring-2 focus:ring-primary-500 focus:border-transparent
                    disabled:opacity-50 disabled:cursor-not-allowed
                    transition-all duration-300 ease-in-out
                    hover:border-gray-400 dark:hover:border-gray-500
                  "
                  placeholder="Enter your email"
                />
              </div>

              <div>
                <label htmlFor="password" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Password
                </label>
                <input
                  type="password"
                  id="password"
                  name="password"
                  value={formData.password}
                  onChange={handleChange}
                  required
                  disabled={isLoading}
                  className="
                    w-full px-4 py-3 rounded-xl border border-gray-300 dark:border-gray-600
                    bg-white dark:bg-gray-800 text-gray-900 dark:text-white
                    placeholder-gray-500 dark:placeholder-gray-400
                    focus:ring-2 focus:ring-primary-500 focus:border-transparent
                    disabled:opacity-50 disabled:cursor-not-allowed
                    transition-all duration-300 ease-in-out
                    hover:border-gray-400 dark:hover:border-gray-500
                  "
                  placeholder="Enter your password"
                />
              </div>
            </div>

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

            <button
              type="submit"
              disabled={isLoading}
              className="
                w-full py-3 px-4 rounded-xl text-white font-semibold
                bg-gradient-to-r from-primary-500 to-accent-500
                hover:from-primary-600 hover:to-accent-600
                focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2
                dark:focus:ring-offset-gray-900
                disabled:opacity-50 disabled:cursor-not-allowed
                transform transition-all duration-300 ease-in-out
                hover:scale-[1.02] active:scale-[0.98]
                shadow-lg hover:shadow-xl
              "
            >
              {isLoading ? (
                <div className="flex items-center justify-center">
                  <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                    <path className="opacity-75" fill="currentColor" d="m4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                  </svg>
                  Signing in...
                </div>
              ) : (
                'Sign in to your journal'
              )}
            </button>
          </form>

          {/* Footer */}
          <div className="text-center pt-4">
            <p className="text-gray-600 dark:text-gray-400">
              Don't have an account?{' '}
              <Link 
                to="/register" 
                className="font-semibold text-primary-600 hover:text-primary-500 dark:text-primary-400 dark:hover:text-primary-300 transition-colors duration-300"
              >
                Sign up now
              </Link>
            </p>
          </div>
        </div>
      </div>

      {/* Right side - Hero Section */}
      <div className="hidden lg:flex lg:flex-1 relative overflow-hidden bg-gradient-to-br from-primary-600 via-primary-700 to-accent-600">
        {/* Background Pattern */}
        <div className="absolute inset-0 opacity-10">
          <div className="absolute inset-0" style={{
            backgroundImage: `url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23ffffff' fill-opacity='1'%3E%3Ccircle cx='7' cy='7' r='2'/%3E%3Ccircle cx='27' cy='7' r='2'/%3E%3Ccircle cx='47' cy='7' r='2'/%3E%3Ccircle cx='7' cy='27' r='2'/%3E%3Ccircle cx='27' cy='27' r='2'/%3E%3Ccircle cx='47' cy='27' r='2'/%3E%3Ccircle cx='7' cy='47' r='2'/%3E%3Ccircle cx='27' cy='47' r='2'/%3E%3Ccircle cx='47' cy='47' r='2'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E")`
          }} />
        </div>

        {/* Content */}
        <div className="relative flex items-center justify-center w-full p-12">
          <div className="max-w-lg text-center text-white">
            <div className="mb-8">
              <div className="inline-flex items-center justify-center w-20 h-20 rounded-full bg-white/20 backdrop-blur-sm mb-6">
                <svg className="w-10 h-10 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z" />
                </svg>
              </div>
              <h2 className="text-4xl font-bold mb-4">
                Your Digital Journal
              </h2>
              <p className="text-xl text-white/90 leading-relaxed">
                Capture your thoughts, track your growth, and discover insights with AI-powered search and reflection.
              </p>
            </div>

            <div className="space-y-4 text-left">
              <div className="flex items-center space-x-3">
                <div className="flex-shrink-0 w-6 h-6 bg-white/20 rounded-full flex items-center justify-center">
                  <svg className="w-3 h-3 text-white" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                  </svg>
                </div>
                <p className="text-white/90">AI-powered smart search</p>
              </div>
              <div className="flex items-center space-x-3">
                <div className="flex-shrink-0 w-6 h-6 bg-white/20 rounded-full flex items-center justify-center">
                  <svg className="w-3 h-3 text-white" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                  </svg>
                </div>
                <p className="text-white/90">Beautiful, distraction-free writing</p>
              </div>
              <div className="flex items-center space-x-3">
                <div className="flex-shrink-0 w-6 h-6 bg-white/20 rounded-full flex items-center justify-center">
                  <svg className="w-3 h-3 text-white" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                  </svg>
                </div>
                <p className="text-white/90">Secure and private</p>
              </div>
            </div>
          </div>
        </div>

        {/* Theme Toggle */}
        <div className="absolute top-6 right-6">
          <ThemeToggle className="bg-white/20 backdrop-blur-sm text-white hover:bg-white/30" />
        </div>
      </div>
    </div>
  );
};

export default LoginPage;
