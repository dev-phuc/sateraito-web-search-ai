import { create } from 'zustand';

// Request client websites list
import { fetchClientWebsitesList, createClientWebsites, editClientWebsites, deleteClientWebsites, getFirebaseTokenForClient } from '@/request/clientWebsites';

const useStoreClientWebsites = create((set) => ({
  // Flag
  isLoading: false,
  isCreating: false,
  isUpdating: false,
  isDeleting: false,
  isFetchingFirebaseToken: false,
  setIsLoading: (loading) => set({ isLoading: loading }),

  // Data
  clientWebsites: [],
  setClientWebsites: (websites) => {
    set({ clientWebsites: websites });
  },

  firebaseToken: null,
  setFirebaseToken: (token) => {
    set({ firebaseToken: token });
  },
  getFirebaseToken: async (tenant, app_id, clientWebsite) => {
    let success, message_result = 'TXT_ERROR_FETCH_FIREBASE_TOKEN';

    set({ isFetchingFirebaseToken: true });
    try {
      const { message, token } = await getFirebaseTokenForClient(tenant, app_id, clientWebsite);
      if (message == 'success') {
        set({ firebaseToken: token });
        success = true;
        message_result = '';
      }
    }
    catch (error) {
      const data = error.response?.data;
      if (data && data.message) message_result = data.message;
      success = false;
      console.error('Error fetching firebase token:', message_result);
    }
    finally {
      set({ isFetchingFirebaseToken: false });
    }

    return { success, message: message_result };
  },

  // Actions
  fetchClientWebsites: async (tenant, app_id) => {
    let success = false, message_result = 'TXT_ERROR_FETCH_CLIENT_WEBSITES';

    set({ isLoading: true });
    try {
      const { message, client_websites } = await fetchClientWebsitesList(tenant, app_id);
      if (message == 'success') {
        set({ clientWebsites: client_websites });
        success = true;
        message_result = '';
      }
    }
    catch (error) {
      const data = error.response?.data;
      if (data && data.message) message_result = data.message;
      console.error('Error fetching client websites:', message_result);
    }
    finally {
      set({ isLoading: false });
    }

    return { success, message: message_result };
  },

  createClientWebsites: async (tenant, app_id, data) => {
    let success = false, message_result = 'TXT_ERROR_CREATE_CLIENT_WEBSITES';

    set({ isCreating: true });
    try {
      const { message, client_website } = await createClientWebsites(tenant, app_id, data);
      if (message == 'success') {
        set((state) => ({
          clientWebsites: [...state.clientWebsites, client_website],
        }));
        success = true;
        message_result = '';
      }
    }
    catch (error) {
      const data = error.response?.data;
      if (data && data.message) message_result = data.message;
      console.error('Error creating client websites:', message_result);
    }
    finally {
      set({ isCreating: false });
    }

    return { success, message: message_result };
  },

  editClientWebsites: async (tenant, app_id, id, data) => {
    let success = false, message_result = 'TXT_ERROR_UPDATE_CLIENT_WEBSITES';

    set({ isUpdating: true });
    try {
      const { message, client_website } = await editClientWebsites(tenant, app_id, id, data);
      if (message == 'success') {
        set((state) => ({
          clientWebsites: state.clientWebsites.map((website) =>
            (website.id === id) ? client_website : website
          ),
        }));
        success = true;
        message_result = '';
      }
    }
    catch (error) {
      const data = error.response?.data;
      if (data && data.message) message_result = data.message;
      console.error('Error updating client websites:', message_result);
    }
    finally {
      set({ isUpdating: false });
    }

    return { success, message: message_result };
  },

  deleteClientWebsites: async (tenant, app_id, id) => {
    let success = false, message_result = 'TXT_ERROR_DELETE_CLIENT_WEBSITES';

    set({ isDeleting: true });
    try {
      const { message } = await deleteClientWebsites(tenant, app_id, id);
      if (message == 'success') {
        set((state) => ({
          clientWebsites: state.clientWebsites.filter((website) => website.id !== id),
        }));
        success = true;
        message_result = '';
      }
    }
    catch (error) {
      const data = error.response?.data;
      if (data && data.message) message_result = data.message;
      console.error('Error deleting client websites:', message_result);
    }
    finally {
      set({ isDeleting: false });
    }

    return { success, message: message_result };
  },
}));

export default useStoreClientWebsites;