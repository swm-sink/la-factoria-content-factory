import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { useNavigate } from 'react-router-dom';
import apiClient from '../api'; // Import the apiClient
import { ApiError } from '../types/content'; // Assuming ApiError is defined for error handling
import { useError } from './ErrorContext'; // Import useError

// Define a User type based on backend response if available, e.g., from app/models/pydantic/user.py UserResponse
interface User {
  id: string;
  email: string;
  // Add other user fields as needed, e.g., full_name, is_active, is_superuser
}

interface AuthContextType {
  isAuthenticated: boolean;
  user: User | null;
  token: string | null;
  isLoading: boolean;
  login: (email_or_username: string, password_string: string) => Promise<void>;
  logout: () => void;
  register: (email_string: string, password_string: string) => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [isAuthenticated, setIsAuthenticated] = useState<boolean>(false);
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const navigate = useNavigate();
  const { setError: setGlobalError } = useError(); // Get setError from ErrorContext

  useEffect(() => {
    const attemptAutoLogin = async () => {
      const storedToken = localStorage.getItem('authToken');
      if (storedToken) {
        setToken(storedToken); // Set token for apiClient to use
        try {
          // apiClient will use the token from localStorage due to the interceptor
          const response = await apiClient.get('/api/v1/auth/users/me');
          setUser(response.data);
          setIsAuthenticated(true);
          console.log('Auto-login successful, user data fetched.');
        } catch (error) {
          console.error('Auto-login failed: Token validation or user fetch failed.', error);
          localStorage.removeItem('authToken'); // Clear invalid token
          setToken(null);
          setUser(null);
          setIsAuthenticated(false);
          // Optionally set a global error for auto-login failure if desired, though often silent failure is preferred
        }
      }
      setIsLoading(false);
    };

    attemptAutoLogin();
  }, []);

  const login = async (email: string, password_string: string) => {
    setIsLoading(true);
    try {
      const response = await apiClient.post(
        '/api/v1/auth/login',
        new URLSearchParams({ username: email, password: password_string }), // FastAPI token endpoint expects form data
        { headers: { 'Content-Type': 'application/x-www-form-urlencoded' }}
      );
      const { access_token } = response.data; // Login endpoint returns only token
      localStorage.setItem('authToken', access_token);
      setToken(access_token);
      setGlobalError(null); // Clear previous errors on successful token fetch

      // After setting token, fetch user details
      try {
        const userResponse = await apiClient.get('/api/v1/auth/users/me'); // apiClient already has /api base
        setUser(userResponse.data);
        setIsAuthenticated(true);
        navigate('/generate'); // Navigate to generate page or dashboard
      } catch (userError) {
        // Handle error fetching user details, maybe logout
        console.error('Failed to fetch user details after login:', userError);
        const castedUserError = userError as ApiError;
        setGlobalError(castedUserError.message || 'Failed to fetch user details after login.');
        localStorage.removeItem('authToken');
        setToken(null);
        setUser(null);
        setIsAuthenticated(false);
        throw userError; // Re-throw to be caught by the form or display a generic error
      }
    } catch (error) {
      const err = error as ApiError;
      console.error('Login failed:', err.message);
      setGlobalError(err.message || 'Login failed. Please check your credentials.');
      throw err; // Re-throw to be caught by the form
    } finally {
      setIsLoading(false);
    }
  };

  const register = async (email_string: string, password_string: string) => {
    setIsLoading(true);
    try {
      // Assuming backend returns UserResponse: { id: string, email: string }
      await apiClient.post('/api/v1/auth/register', {
        email: email_string,
        password: password_string,
      });
      // After successful registration, typically navigate to login or show success message
      // For now, just log success. User will need to login separately.
      console.log('Registration successful for:', email_string);
      setGlobalError(null); // Clear previous errors
      navigate('/login?registered=true'); // Optionally redirect to login with a success indicator
    } catch (error) {
      const err = error as ApiError;
      console.error('Registration failed:', err.message);
      setGlobalError(err.message || 'Registration failed. Please try again.');
      throw err; // Re-throw to be caught by the form
    } finally {
      setIsLoading(false);
    }
  };

  const logout = () => {
    localStorage.removeItem('authToken');
    setToken(null);
    setUser(null);
    setIsAuthenticated(false);
    console.log('AuthContext: Logged out');
    navigate('/'); // Redirect to home page after logout
  };

  return (
    <AuthContext.Provider value={{ isAuthenticated, user, token, isLoading, login, logout, register }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
