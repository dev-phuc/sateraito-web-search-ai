import { create } from 'zustand';

// Requests
import { getTenantConfig, updateTenantConfig } from '@/request/TenantConfig';

const useStoreTenantConfig = create((set) => ({
  // Flags
  loading: false,
  error: null,
  loaded: false,

  // Data
  contractInformation: null,
  llmQuota: null,
  otherSetting: null,

  // Actions
  setLoading: (loading) => set({ loading }),
  setError: (error) => set({ error }),

  setContractInformation: (info) => set({ contractInformation: info }),
  setLlmQuota: (quota) => set({ llmQuota: quota }),
  setOtherSetting: (setting) => set({ otherSetting: setting }),

  // Fetch tenant configuration
  fetchTenantConfig: async (tenant, app_id) => {
    set({ loading: true, error: null });
    try {
      const data = await getTenantConfig(tenant, app_id);
      set({
        contractInformation: data.contract_information,
        llmQuota: data.llm_quota,
        otherSetting: data.other_setting,
        loading: false,
        loaded: true,
      });
    } catch (error) {
      set({ error: error.message || 'Failed to fetch tenant configuration', loading: false });
    }
  },

  // Update tenant configuration
  updateTenantConfig: async (tenant, app_id, newData) => {
    set({ loading: true, error: null });
    try {
      const data = await updateTenantConfig(tenant, app_id, newData);
      set({
        contractInformation: data.contractInformation,
        llmQuota: data.llmQuota,
        otherSetting: data.otherSetting,
        loading: false,
      });
    } catch (error) {
      set({ error: error.message || 'Failed to update tenant configuration', loading: false });
    } 
  },

}));

export default useStoreTenantConfig;