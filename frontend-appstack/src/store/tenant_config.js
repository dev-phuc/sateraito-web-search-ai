import { create } from 'zustand';

// Requests
import { getTenantConfig, updateContractInfo } from '@/request/TenantConfig';

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
    let success = false, message_result = 'TXT_ERROR_GET_TENANT_CONFIG';

    set({ loading: true, error: null });
    try {
      const { message, tenant_config } = await getTenantConfig(tenant, app_id);
      if (message == 'success' && tenant_config) {
        set({
          contractInformation: tenant_config.contract_information,
          llmQuota: tenant_config.llm_quota,
          otherSetting: tenant_config.other_setting,
          loading: false,
          loaded: true,
        });
        success = true;
        message_result = '';
      }
    } catch (error) {
      const { response } = error;
      const errorMessage = response?.data?.message || error.message || 'Failed to fetch tenant configuration';
      message_result = errorMessage;
    }
    finally {
      set({ loading: false });
    }

    return { success, message: message_result };
  },

  // Update tenant configuration
  updateContractInfo: async (tenant, app_id, contractInfo) => {
    try {
      const { message } = await updateContractInfo(tenant, app_id, contractInfo);
      if (message == 'success') {
        set({ contractInformation: { ...contractInfo } });
        return { success: true };
      }
      return { success: false, error: message || 'Failed to update contract information' };
    } catch (error) {
      const { response } = error;
      const errorMessage = response?.data?.message || error.message || 'Failed to update contract information';
      return { success: false, error: errorMessage };
    }
  },
}));

export default useStoreTenantConfig;