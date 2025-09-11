import { create } from 'zustand';

// Request llm configuration
import { getLLMConfiguration, getLLMConfigurationForClient, editLLMConfiguration } from '@/request/LLMConfiguration';

const useStoreLLMConfiguration = create((set) => ({
  // Flag
  isLoading: false,
  setIsLoading: (loading) => set({ isLoading: loading }),

  // Data
  llmConfiguration: null,
  setLLMConfiguration: (llmConfiguration) => {
    set({ llmConfiguration });
  },
  getLLMConfiguration: async (tenant, app_id) => {
    set({ isLoading: true });

    try {
      const llmConfiguration = await getLLMConfiguration(tenant, app_id);
      set({ llmConfiguration });
    }
    catch (error) {
      console.error('Error fetching LLM configuration:', error);
    }
    finally {
      set({ isLoading: false });
    }
  },

  llmConfigurationForClient: null,
  setLLMConfigurationForClient: (llmConfigurationForClient) => {
    set({ llmConfigurationForClient });
  },
  getLLMConfigurationForClient: async (tenant, app_id, clientWebsite) => {
    set({ isLoading: true });
    try {
      const llmConfigurationForClient = await getLLMConfigurationForClient(tenant, app_id, clientWebsite);
      set({ llmConfigurationForClient });
    }
    catch (error) {
      console.error('Error fetching LLM configuration for client:', error);
    }
    finally {
      set({ isLoading: false });
    }
  },
  
  // Actions
  editLLMConfiguration: async (tenant, app_id, config) => {
    try {
      const updated = await editLLMConfiguration(tenant, app_id, { config: config });
      return { success: true, data: updated };
    }
    catch (error) {
      const data = error.response?.data;
      let key_message_error = 'TXT_ERROR_UPDATE_LLM_CONFIGURATION';
      if (data && data.message) {
        key_message_error = data.message;
      }
      return { success: false, error: key_message_error };
    }
  },
}));

export default useStoreLLMConfiguration;