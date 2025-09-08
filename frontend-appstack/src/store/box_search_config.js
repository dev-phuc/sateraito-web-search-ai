import { create } from 'zustand';

// Request box search config
import { getBoxSearchConfig, editBoxSearchConfig } from '@/request/boxSearchConfig';

const useStoreBoxSearchConfig = create((set) => ({
  // Flag
  isLoading: false,
  setIsLoading: (loading) => set({ isLoading: loading }),

  // Data
  boxSearchConfig: null,
  setBoxSearchConfig: (boxSearchConfig) => {
    set({ boxSearchConfig });
  },
  boxSearchConfigPreview: null,
  setBoxSearchConfigPreview: (boxSearchConfigPreview) => {
    set({ boxSearchConfigPreview });
  },

  // Actions
  getBoxSearchConfig: async (tenant, app_id) => {
    set({ isLoading: true });

    try {
      const boxSearchConfig = await getBoxSearchConfig(tenant, app_id);
      set({ boxSearchConfig });
    }
    catch (error) {
      console.error('Error fetching box search config:', error);
    }
    finally {
      set({ isLoading: false });
    }
  },

  editBoxSearchConfig: async (tenant, app_id, config) => {
    try {
      const updated = await editBoxSearchConfig(tenant, app_id, { config: config });
      return { success: true, data: updated };
    }
    catch (error) {
      const data = error.response?.data;
      let key_message_error = 'TXT_ERROR_UPDATE_BOX_SEARCH_CONFIG';
      if (data && data.message) {
        key_message_error = data.message;
      }
      return { success: false, error: key_message_error };
    }
  },
}));

export default useStoreBoxSearchConfig;