import create, { SetState } from 'zustand';

interface ApiKeyState {
  apiKey: string;
  setApiKey: (key: string) => void;
}

export const useApiKeyStore = create<ApiKeyState>((set: SetState<ApiKeyState>) => ({
  apiKey: localStorage.getItem('apiKey') || '',
  setApiKey: (key: string) => {
    localStorage.setItem('apiKey', key);
    set({ apiKey: key });
  },
})); 