import { create } from 'zustand';

// Request llm configuration
import { getLLMConfiguration, getLLMConfigurationForClient, editLLMConfiguration } from '@/request/LLMConfiguration';

const useStoreLLMConfiguration = create((set) => ({
  // Flag
  isLoading: false,
  isUpdating: false,
  setIsLoading: (loading) => set({ isLoading: loading }),

  // Data
  llmConfiguration: null,
  setLLMConfiguration: (llmConfiguration) => {
    set({ llmConfiguration });
  },
  getLLMConfiguration: async (tenant, app_id) => {
    let success = false, message_result = 'TXT_ERROR_GET_LLM_CONFIGURATION';

    set({ isLoading: true });
    try {
      const { message, config } = await getLLMConfiguration(tenant, app_id);
      if (message == 'success') {
        set({ llmConfiguration: config });
        success = true;
        message_result = '';
      }
    }
    catch (error) {
      const data = error.response?.data;
      if (data && data.message) message_result = data.message;
      console.error('Error fetching LLM configuration:', message_result);
    }
    finally {
      set({ isLoading: false });
    }

    return { success, message: message_result };
  },

  llmConfigurationForClient: null,
  setLLMConfigurationForClient: (llmConfigurationForClient) => {
    set({ llmConfigurationForClient });
  },
  getLLMConfigurationForClient: async (tenant, app_id, clientWebsite) => {
    let success = false, message_result = 'TXT_ERROR_GET_LLM_CONFIGURATION';

    set({ isLoading: true });
    try {
      const { message, config } = await getLLMConfigurationForClient(tenant, app_id, clientWebsite);
      if (message == 'success') {
        set({ llmConfigurationForClient: config });
        success = true;
        message_result = '';
      }
    }
    catch (error) {
      const data = error.response?.data;
      if (data && data.message) message_result = data.message;
      console.error('Error fetching LLM configuration for client:', message_result);
    }
    finally {
      set({ isLoading: false });
    }
    return { success, message: message_result };
  },
  
  // Actions
  editLLMConfiguration: async (tenant, app_id, config) => {
    let success = false, message_result = 'TXT_ERROR_UPDATE_LLM_CONFIGURATION';

    set({ isUpdating: true });
    try {
      const { message } = await editLLMConfiguration(tenant, app_id, { config: config });
      if (message == 'success') {
        success = true;
        message_result = '';
      }
    }
    catch (error) {
      const data = error.response?.data;
      if (data && data.message) message_result = data.message;
      console.error('Error updating LLM configuration:', message_result);
    }
    finally {
      set({ isUpdating: false });
    }

    return { success, message: message_result };
  },
}));

export default useStoreLLMConfiguration;