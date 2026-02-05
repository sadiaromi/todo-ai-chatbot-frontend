// Simple auth implementation that mimics Better Auth's interface
// for development purposes until Better Auth issues are resolved
'use client';

import { useState, useEffect } from 'react';

// Simple state for session management
let _session: any = null;
let _loading: boolean = true;

// Custom hook for session
export const useSession = () => {
  const [session, setSession] = useState(_session);
  const [loading, setLoading] = useState(_loading);

  useEffect(() => {
    // Simulate checking session on mount
    const checkSession = async () => {
      // Check if user is logged in by checking localStorage
      const user = localStorage.getItem('user');
      if (user) {
        try {
          const userData = JSON.parse(user);
          _session = { user: userData };
          _loading = false;
          setSession({ user: userData });
          setLoading(false);
        } catch (error) {
          _session = null;
          _loading = false;
          setSession(null);
          setLoading(false);
        }
      } else {
        _session = null;
        _loading = false;
        setSession(null);
        setLoading(false);
      }
    };

    if (_loading) {
      checkSession();
    } else {
      setSession(_session);
      setLoading(_loading);
    }
  }, []);

  return { data: session, isLoading: loading };
};

// Helper function to generate a random UUID
function generateUUID(): string {
  return '123e4567-e89b-12d3-a456-426614174000'; // Use consistent UUID for demo
}

// Sign in function
export const signIn = {
  email: async ({ email, password, redirect }: { email: string; password: string; redirect: boolean }) => {
    // Simulate sign in - in a real app, this would call your backend
    const user = { id: generateUUID(), email, name: email.split('@')[0] };
    localStorage.setItem('user', JSON.stringify(user));
    _session = { user };
    _loading = false;

    if (redirect) {
      window.location.href = '/';
    }

    return { user };
  }
};

// Sign up function
export const signUp = {
  email: async ({ email, password, name, redirect }: { email: string; password: string; name: string; redirect: boolean }) => {
    // Simulate sign up - in a real app, this would call your backend
    const user = { id: generateUUID(), email, name };
    localStorage.setItem('user', JSON.stringify(user));
    _session = { user };
    _loading = false;

    if (redirect) {
      window.location.href = '/';
    }

    return { user };
  }
};

// Sign out function
export const signOut = async () => {
  localStorage.removeItem('user');
  _session = null;
  window.location.href = '/login';
};

// Simple AuthProvider component
export const AuthProvider = ({ children }: { children: React.ReactNode }) => children;