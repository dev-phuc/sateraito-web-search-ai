import { create } from 'zustand';

// Request usage logs
import { fetchLLMUsage } from '@/request/LLMUsage';

const useStoreLLMUsage = create((set) => ({
  // Flag
  isLoading: false,
  setIsLoading: (loading) => set({ isLoading: loading }),

  // Data
  llmUsage: null,
  llmUsageLastMonth: null,
  setLLMUsage: (usage) => {
    set({ llmUsage: usage });
  },

  // Actions
  fetchLLMUsage: async (tenant, app_id, timeFrame) => {
    set({ isLoading: true });

    try {
      const params = {
        time_frame: timeFrame || 'month',
      };
      const result = await fetchLLMUsage(tenant, app_id, params);
      if (result) {
        set({ llmUsage: result });
      }
    }
    catch (error) {
      console.error('Error fetching operation logs:', error);
      set({ llmUsage: {} });
    }
    finally {
      set({ isLoading: false });
    }
  },

  fetchLLMUsageLastMonth: async (tenant, app_id) => {
    set({ isLoading: true });

    try {
      const params = {
        time_frame: 'last_month',
      };
      const result = await fetchLLMUsage(tenant, app_id, params);
      if (result) {
        set({ llmUsageLastMonth: result });
      }
    }
    catch (error) {
      console.error('Error fetching operation logs:', error);
      set({ llmUsageLastMonth: {} });
    }
    finally {
      set({ isLoading: false });
    }
  },

}));

export default useStoreLLMUsage;