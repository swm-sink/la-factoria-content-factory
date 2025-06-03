// Axios client configuration for API communication
// Sets up a base URL and request interceptors for adding API key and JWT token.
import axios from 'axios';
import { useApiKeyStore } from './store/useApiKeyStore';

const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api/v1', // Use VITE_API_BASE_URL, fallback to /api/v1
  headers: {
    'Content-Type': 'application/json',
  },
});

apiClient.interceptors.request.use((config: any) => {
  const apiKey = useApiKeyStore.getState().apiKey;
  // Ensure headers object exists
  config.headers = config.headers || {};
  if (apiKey) {
    config.headers['X-API-Key'] = apiKey;
  }
  // Add JWT token if available
  const token = localStorage.getItem('authToken');
  if (token) {
    config.headers['Authorization'] = `Bearer ${token}`;
  }
  return config;
});

export default apiClient;
