import { create } from 'zustand';
import { aiAPI } from '../services/api';

const useSearchStore = create((set, get) => ({
  searchResult: null,
  isLoading: false,
  error: null,
  searchHistory: [],

  search: async (query) => {
    if (!query.trim()) return;
    
    set({ isLoading: true, error: null });
    try {
      const response = await aiAPI.search(query);
      const result = {
        query,
        response: response.data.response,
        relevantEntriesCount: response.data.relevant_entries_count,
        timestamp: new Date().toISOString(),
      };
      
      set((state) => ({
        searchResult: result,
        searchHistory: [result, ...state.searchHistory.slice(0, 9)], // Keep last 10 searches
        isLoading: false,
      }));
      
      return { success: true };
    } catch (error) {
      const errorMessage = error.response?.data?.error || 'Search failed';
      set({ error: errorMessage, isLoading: false });
      return { success: false, error: errorMessage };
    }
  },

  clearSearch: () => set({ searchResult: null, error: null }),
  
  clearError: () => set({ error: null }),
}));

export default useSearchStore;
