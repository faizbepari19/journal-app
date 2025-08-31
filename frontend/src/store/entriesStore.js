import { create } from 'zustand';
import { entriesAPI } from '../services/api';

const useEntriesStore = create((set, get) => ({
  entries: [],
  isLoading: false,
  error: null,

  fetchEntries: async () => {
    set({ isLoading: true, error: null });
    try {
      const response = await entriesAPI.getEntries();
      set({ entries: response.data.entries, isLoading: false });
    } catch (error) {
      const errorMessage = error.response?.data?.error || 'Failed to fetch entries';
      set({ error: errorMessage, isLoading: false });
    }
  },

  createEntry: async (content) => {
    set({ isLoading: true, error: null });
    try {
      const response = await entriesAPI.createEntry({ content });
      const newEntry = response.data.entry;
      
      set((state) => ({
        entries: [newEntry, ...state.entries],
        isLoading: false,
      }));
      
      return { success: true };
    } catch (error) {
      const errorMessage = error.response?.data?.error || 'Failed to create entry';
      set({ error: errorMessage, isLoading: false });
      return { success: false, error: errorMessage };
    }
  },

  updateEntry: async (entryId, content) => {
    set({ isLoading: true, error: null });
    try {
      const response = await entriesAPI.updateEntry(entryId, { content });
      const updatedEntry = response.data.entry;
      
      set((state) => ({
        entries: state.entries.map((entry) =>
          entry.id === entryId ? updatedEntry : entry
        ),
        isLoading: false,
      }));
      
      return { success: true };
    } catch (error) {
      const errorMessage = error.response?.data?.error || 'Failed to update entry';
      set({ error: errorMessage, isLoading: false });
      return { success: false, error: errorMessage };
    }
  },

  deleteEntry: async (entryId) => {
    set({ isLoading: true, error: null });
    try {
      await entriesAPI.deleteEntry(entryId);
      
      set((state) => ({
        entries: state.entries.filter((entry) => entry.id !== entryId),
        isLoading: false,
      }));
      
      return { success: true };
    } catch (error) {
      const errorMessage = error.response?.data?.error || 'Failed to delete entry';
      set({ error: errorMessage, isLoading: false });
      return { success: false, error: errorMessage };
    }
  },

  clearError: () => set({ error: null }),
}));

export default useEntriesStore;
