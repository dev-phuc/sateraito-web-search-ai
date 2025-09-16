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
    set({ isLoading: true });

    try {
      const params = {
        page: page || 1,
        limit: limit || 20,
        ...paramsSearch
      };
      const result = await fetchOperationLogs(tenant, app_id, params);
      if (result) {
        const { total_rows, have_more_rows, operation_logs } = result;
        set({ operationLogs: operation_logs });
        set({ total: total_rows });
        set({ isHaveMore: have_more_rows });
      }
    }
    catch (error) {
      console.error('Error fetching operation logs:', error);
      set({ operationLogs: [] });
      set({ total: 0 });
      set({ isHaveMore: false });
    }
    finally {
      set({ isLoading: false });
    }
  },
}));

export default useStoreOperationLogs;