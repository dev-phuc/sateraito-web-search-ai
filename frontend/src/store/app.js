import { create } from 'zustand';

const useStoreApp = create((set) => ({
  sidebarClosed: false,

  toggleSidebar: () => {
    set((state) => {
      const newState = !state.sidebarClosed;
      // Save to storage
      localStorage.setItem('sidebarClosed', newState);
      return { sidebarClosed: newState };
    });
  },
  setSidebarClosed: (closed) => {
    set({ sidebarClosed: closed });
    // Save to storage
    localStorage.setItem('sidebarClosed', closed);
  },
}));

export default useStoreApp;