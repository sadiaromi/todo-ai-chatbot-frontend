import { useState, useEffect } from 'react';
import { auth } from './lib/auth';

export const useAuth = () => {
  const [user, setUser] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const checkAuth = async () => {
      try {
        const userData = await auth.getCurrentUser();
        setUser(userData);
      } catch (error) {
        console.error('Auth check failed:', error);
        setUser(null);
      } finally {
        setLoading(false);
      }
    };

    checkAuth();
  }, []);

  const login = async (email: string, password: string) => {
    try {
      const response = await auth.signInWithEmailAndPassword({
        email,
        password,
      });

      if (response?.user) {
        setUser(response.user);
        return { success: true, user: response.user };
      }

      return { success: false, error: 'Login failed' };
    } catch (error) {
      console.error('Login error:', error);
      return { success: false, error: error instanceof Error ? error.message : 'Login failed' };
    }
  };

  const register = async (email: string, password: string, username: string) => {
    try {
      const response = await auth.signUpWithEmailAndPassword({
        email,
        password,
        name: username,
      });

      if (response?.user) {
        setUser(response.user);
        return { success: true, user: response.user };
      }

      return { success: false, error: 'Registration failed' };
    } catch (error) {
      console.error('Registration error:', error);
      return { success: false, error: error instanceof Error ? error.message : 'Registration failed' };
    }
  };

  const logout = async () => {
    try {
      await auth.signOut();
      setUser(null);
    } catch (error) {
      console.error('Logout error:', error);
    }
  };

  return {
    user,
    loading,
    login,
    register,
    logout,
  };
};