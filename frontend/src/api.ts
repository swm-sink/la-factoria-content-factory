import axios, { AxiosRequestConfig } from 'axios';
import { useApiKeyStore } from './store/useApiKeyStore';

const api = axios.create({
  baseURL: '/api',
  headers: {
    'Content-Type': 'application/json',
  },
});

api.interceptors.request.use((config: AxiosRequestConfig) => {
  const apiKey = useApiKeyStore.getState().apiKey;
  if (!config.headers) {
    config.headers = {};
  }
  if (apiKey) {
    config.headers['X-API-Key'] = apiKey;
  }
  return config;
});

export default api; 