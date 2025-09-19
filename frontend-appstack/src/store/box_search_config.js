import { create } from 'zustand';

// Request box search config
import { getBoxSearchConfig, getBoxSearchConfigForClient, editBoxSearchConfig } from '@/request/boxSearchConfig';

const useStoreBoxSearchConfig = create((set) => ({
  // Flag
  isLoading: false,
  setIsLoading: (loading) => set({ isLoading: loading }),

  // Data
  boxSearchConfig: null,
  setBoxSearchConfig: (boxSearchConfig) => {
    set({ boxSearchConfig });
  },
  getBoxSearchConfig: async (tenant, app_id) => {
    let success = false, message_result = 'TXT_ERROR_GET_BOX_SEARCH_CONFIG';

    set({ isLoading: true });
    try {
      const { message, config } = await getBoxSearchConfig(tenant, app_id);
      if (message == 'success') {
        set({ boxSearchConfig: config });
        success = true;
        message_result = '';
      }
    }
    catch (error) {
      const data = error.response?.data;
      if (data && data.message) message_result = data.message;
      console.error('Error fetching box search config:', message);
    }
    finally {
      set({ isLoading: false });
    }

    return { success, message: message_result };
  },

  boxSearchConfigPreview: null,
  setBoxSearchConfigPreview: (boxSearchConfigPreview) => {
    set({ boxSearchConfigPreview });
  },

  boxSearchConfigForClient: null,
  setBoxSearchConfigForClient: (boxSearchConfigForClient) => {
    set({ boxSearchConfigForClient });
  },
  getBoxSearchConfigForClient: async (tenant, app_id, clientWebsite) => {
    let success = false, message_result = 'TXT_ERROR_GET_BOX_SEARCH_CONFIG';
    set({ isLoading: true });
    try {
      const { message, config } = await getBoxSearchConfigForClient(tenant, app_id, clientWebsite);
      if (message == 'success') {
        set({ boxSearchConfigForClient: config });
        success = true;
        message_result = '';
      }
    }
    catch (error) {
      const data = error.response?.data;
      if (data && data.message) message_result = data.message;
      console.error('Error fetching box search config for client:', message);
    }
    finally {
      set({ isLoading: false });
    }

    return { success, message: message_result };
  },

  // Actions
  editBoxSearchConfig: async (tenant, app_id, config) => {
    let success = false, message_result = 'TXT_ERROR_UPDATE_BOX_SEARCH_CONFIG';

    set({ isLoading: true });
    try {
      const { message } = await editBoxSearchConfig(tenant, app_id, { config: config });
      if (message == 'success') {
        success = true;
        message_result = '';
      }
    }
    catch (error) {
      const data = error.response?.data;
      if (data && data.message) message_result = data.message;
      console.error('Error updating box search config:', message);
    }
    finally {
      set({ isLoading: false });
    }

    return { success, message: message_result };
  },
}));

export default useStoreBoxSearchConfig;