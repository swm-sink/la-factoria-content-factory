import { create } from 'zustand';

export const useApiKeyStore = create((set: any) => ({
  apiKey: localStorage.getItem('apiKey') || '',
  setApiKey: (key: string) => {
    localStorage.setItem('apiKey', key);
    set({ apiKey: key });
  },
}));
