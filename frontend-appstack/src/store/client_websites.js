import { create } from 'zustand';

// Request client websites list
import { fetchClientWebsitesList, createClientWebsites, editClientWebsites, deleteClientWebsites } from '@/request/clientWebsites';

const useStoreClientWebsites = create((set) => ({
  // Flag
  isLoading: false,
  setIsLoading: (loading) => set({ isLoading: loading }),

  // Data
  clientWebsites: [],
  setClientWebsites: (websites) => {
    set({ clientWebsites: websites });
  },

  // Actions
  fetchClientWebsites: async (tenant, app_id) => {
    set({ isLoading: true });

    try {
      const websites = await fetchClientWebsitesList(tenant, app_id);
      set({ clientWebsites: websites });
    }
    catch (error) {
      console.error('Error fetching client websites:', error);
    }
    finally {
      set({ isLoading: false });
    }
  },

  createClientWebsites: async (tenant, app_id, data) => {
    try {
      const newWebsite = await createClientWebsites(tenant, app_id, data);
      set((state) => ({
        clientWebsites: [...state.clientWebsites, newWebsite],
      }));

      return {success: true, data: newWebsite};
    }
    catch (error) {
      const data = error.response?.data;

      let key_message_error = 'TXT_ERROR_CREATE_CLIENT_WEBSITES';
      if (data && data.message) {
        key_message_error = data.message;
      }

      return {success: false, error: key_message_error};
    }
  },

  editClientWebsites: async (tenant, app_id, id, data) => {
    try {
      const updatedWebsite = await editClientWebsites(tenant, app_id, id, data);
      set((state) => ({
        clientWebsites: state.clientWebsites.map((website) =>
          website.id === id ? updatedWebsite : website
        ),
      }));
      return {success: true, data: updatedWebsite};
    }
    catch (error) {
      const data = error.response?.data;
      let key_message_error = 'TXT_ERROR_UPDATE_CLIENT_WEBSITES';
      if (data && data.message) {
        key_message_error = data.message;
      }
      return {success: false, error: key_message_error};
    }
  },

  deleteClientWebsites: async (tenant, app_id, id) => {
    try {
      // Set loading state
      set({ isLoading: true });

      await deleteClientWebsites(tenant, app_id, id);
      set((state) => ({
        clientWebsites: state.clientWebsites.filter((website) => website.id !== id),
      }));
      return {success: true};
    }
    catch (error) {
      const data = error.response?.data;
      let key_message_error = 'TXT_ERROR_DELETE_CLIENT_WEBSITES';
      if (data && data.message) {
        key_message_error = data.message;
      }
      return {success: false, error: key_message_error};
    }
    finally {
      // Clear loading state
      set({ isLoading: false });
    }
  },
}));

export default useStoreClientWebsites;