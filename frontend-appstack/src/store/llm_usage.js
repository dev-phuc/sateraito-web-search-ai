import { create } from 'zustand';

// Request usage logs
import { fetchLLMUsage } from '@/request/LLMUsage';

const useStoreLLMUsage = create((set) => ({
  // Flag
  isLoading: false,
  isLoadingLastMonth: false,
  setIsLoading: (loading) => set({ isLoading: loading }),

  // Data
  llmUsage: null,
  llmUsageLastMonth: null,
  setLLMUsage: (usage) => {
    set({ llmUsage: usage });
  },

  // Actions
  fetchLLMUsage: async (tenant, app_id, timeFrame) => {
    let success = false, message_result = 'TXT_ERROR_GET_LLM_USAGE';

    set({ isLoading: true });
    try {
      const params = {
        time_frame: timeFrame || 'month',
      };
      const { message, usage_data } = await fetchLLMUsage(tenant, app_id, params);
      if (message == 'success') {
        set({ llmUsage: usage_data });
        success = true;
        message_result = '';
      }
    }
    catch (error) {
      const data = error.response?.data;
      if (data && data.message) message_result = data.message;
      console.error('Error fetching LLM usage:', message_result);
    }
    finally {
      set({ isLoading: false });
    }

    return { success, message: message_result };
  },

  fetchLLMUsageLastMonth: async (tenant, app_id) => {
    let success = false, message_result = 'TXT_ERROR_GET_LLM_USAGE';

    set({ isLoadingLastMonth: true });
    try {
      const params = {
        time_frame: 'last_month',
      };
      const { message, usage_data } = await fetchLLMUsage(tenant, app_id, params);
      if (message == 'success') {
        set({ llmUsageLastMonth: usage_data });
        success = true;
        message_result = '';
      }
    }
    catch (error) {
      const data = error.response?.data;
      if (data && data.message) message_result = data.message;
      console.error('Error fetching LLM usage for last month:', message_result);
    }
    finally {
      set({ isLoadingLastMonth: false });
    }

    return { success, message: message_result };
  },

}));

export default useStoreLLMUsage;