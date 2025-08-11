"use client";

import { createContext, useContext, useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { toast } from 'react-hot-toast';

const AuthContext = createContext({});

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const router = useRouter();

  useEffect(() => {
    checkUser();
  }, []);

  const checkUser = async () => {
    try {
      const token = localStorage.getItem('token');
      if (!token) {
        setLoading(false);
        return;
      }

      const response = await fetch('http://localhost:8000/me', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (response.ok) {
        const userData = await response.json();
        setUser({ 
          ...userData, 
          token, 
          email_verified: true,
          type: userData.type || userData.organization_type // Handle both response formats
        });
      } else {
        localStorage.removeItem('token');
        setUser(null);
        toast.error('Session expired. Please login again.');
      }
    } catch (error) {
      console.error('Error checking user:', error);
      localStorage.removeItem('token');
      setUser(null);
      toast.error('Error checking authentication status');
    } finally {
      setLoading(false);
    }
  };

  const login = async (email, password) => {
    try {
      const formData = new FormData();
      formData.append('email', email);
      formData.append('password', password);

      const response = await fetch('http://localhost:8000/login', {
        method: 'POST',
        body: formData
      });

      const data = await response.json();

      if (response.ok) {
        // Get user details after successful login
        const userResponse = await fetch('http://localhost:8000/me', {
          headers: {
            'Authorization': `Bearer ${data.access_token}`
          }
        });

        if (!userResponse.ok) {
          throw new Error('Failed to fetch user details');
        }

        const userData = await userResponse.json();
        
        // Store token and set user state with complete information
        localStorage.setItem('token', data.access_token);
        setUser({ 
          ...userData,
          token: data.access_token,
          email_verified: true,
          type: userData.type || userData.organization_type // Handle both response formats
        });

        toast.success('Welcome back! Login successful', {
          duration: 3000,
        });
        router.push('/dashboard');
      } else {
        // Handle FastAPI validation errors
        if (response.status === 422 && Array.isArray(data.detail)) {
          const errorMessages = data.detail.map(err => err.msg || err.message || JSON.stringify(err)).join(', ');
          throw new Error(errorMessages);
        }
        // Handle other types of errors
        const errorMessage = typeof data.detail === 'string' ? data.detail : 'Login failed';
        throw new Error(errorMessage);
      }
    } catch (error) {
      console.error('Login error:', error);
      toast.error(error.message || 'An error occurred during login', {
        duration: 3000,
      });
      throw error;
    }
  };

  const logout = () => {
    localStorage.removeItem('token');
    setUser(null);
    toast.success('Logged out successfully', {
      duration: 3000,
    });
    router.push('/login');
  };

  const refreshToken = async () => {
    try {
      const token = localStorage.getItem('token');
      if (!token) {
        throw new Error('No token found');
      }

      const response = await fetch('http://localhost:8000/refresh', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (!response.ok) {
        throw new Error('Token refresh failed');
      }

      const data = await response.json();
      localStorage.setItem('token', data.access_token);
      
      // Get updated user details
      const userResponse = await fetch('http://localhost:8000/me', {
        headers: {
          'Authorization': `Bearer ${data.access_token}`
        }
      });

      if (!userResponse.ok) {
        throw new Error('Failed to fetch user details');
      }

      const userData = await userResponse.json();
      setUser(prev => ({ 
        ...prev, 
        ...userData,
        token: data.access_token, 
        email_verified: true,
        type: userData.type || userData.organization_type // Handle both response formats
      }));
      return true;
    } catch (error) {
      console.error('Token refresh failed:', error);
      toast.error('Session expired. Please login again.');
      logout();
      return false;
    }
  };

  const value = {
    user,
    loading,
    login,
    logout,
    refreshToken,
    checkUser,
    updateUser: (userData) => {
      console.log('Updating user with:', userData);
      setUser(prev => ({
        ...prev,
        ...userData,
        type: userData.type || userData.organization_type, // Handle both response formats
        email_verified: true
      }));
    }
  };

  return (
    <AuthContext.Provider value={value}>
      {!loading && children}
    </AuthContext.Provider>
  );
}

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}; 