import { create } from 'zustand';

// Request operation logs
import { fetchOperationLogs } from '@/request/OperationLog';

const useStoreOperationLogs = create((set) => ({
  // Flag
  isLoading: false,
  setIsLoading: (loading) => set({ isLoading: loading }),

  // Data
  isHaveMore: false,
  total: 0,
  operationLogs: [],
  setOperationLogs: (logs) => {
    set({ operationLogs: logs });
  },

  // Actions
  fetchOperationLogs: async (tenant, app_id, page, limit, paramsSearch) => {
    let success = false, message_result = 'TXT_ERROR_GET_OPERATION_LOGS';

    set({ isLoading: true });
    try {
      const params = {
        page: page || 1,
        limit: limit || 20,
        ...paramsSearch
      };
      const { message, logs_data } = await fetchOperationLogs(tenant, app_id, params);
      if (message == 'success') {
        const { total_rows, have_more_rows, operation_logs } = logs_data;
        set({ operationLogs: operation_logs });
        set({ total: total_rows });
        set({ isHaveMore: have_more_rows });
        success = true;
        message_result = '';
      }
    }
    catch (error) {
      const data = error.response?.data;
      if (data && data.message) message_result = data.message;
      console.error('Error fetching operation logs:', error);
      set({ operationLogs: [] });
      set({ total: 0 });
      set({ isHaveMore: false });
    }
    finally {
      set({ isLoading: false });
    }

    return { success, message: message_result };
  },
}));

export default useStoreOperationLogs;