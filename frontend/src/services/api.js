import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000/api';

// Create axios instance
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add request interceptor to include JWT token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Add response interceptor to handle token expiration
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Don't redirect if we're already on login page or if this is a login attempt
      const isLoginRequest = error.config?.url?.includes('/auth/login');
      const isAlreadyOnLoginPage = window.location.pathname === '/login';
      
      if (!isLoginRequest && !isAlreadyOnLoginPage) {
        localStorage.removeItem('access_token');
        localStorage.removeItem('user');
        window.location.href = '/login';
      } else if (isLoginRequest) {
        // For login requests, just clear any stale tokens but don't redirect
        localStorage.removeItem('access_token');
        localStorage.removeItem('user');
      }
    }
    return Promise.reject(error);
  }
);

// Auth API
export const authAPI = {
  register: (userData) => api.post('/auth/register', userData),
  login: (credentials) => api.post('/auth/login', credentials),
  getProfile: () => api.get('/auth/profile'),
};

// Entries API
export const entriesAPI = {
  getEntries: () => api.get('/entries'),
  createEntry: (entryData) => api.post('/entries', entryData),
  updateEntry: (entryId, entryData) => api.put(`/entries/${entryId}`, entryData),
  deleteEntry: (entryId) => api.delete(`/entries/${entryId}`),
};

// AI Search API
export const aiAPI = {
  search: (query) => api.post('/search', { query }),
  testAI: () => api.get('/search/test'),
};

export default api;
