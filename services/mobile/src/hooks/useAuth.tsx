import React, { createContext, useContext, useEffect, useState } from 'react';
import * as SecureStore from 'expo-secure-store';
import { loginApi, registerApi } from '../api/auth';

const TOKEN_KEY = 'access_token';

type AuthContextType = {
  token: string | null;
  isLoading: boolean;
  login: (username: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
  register: (username: string, email: string, password: string) => Promise<void>;
};

const AuthContext = createContext<AuthContextType | null>(null);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [token, setToken] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    SecureStore.getItemAsync(TOKEN_KEY)
      .then((stored) => setToken(stored))
      .finally(() => setIsLoading(false));
  }, []);

  const login = async (username: string, password: string): Promise<void> => {
    const accessToken = await loginApi(username, password);
    await SecureStore.setItemAsync(TOKEN_KEY, accessToken);
    setToken(accessToken);
  };

  const logout = async (): Promise<void> => {
    await SecureStore.deleteItemAsync(TOKEN_KEY);
    setToken(null);
  };

  const register = async (username: string, email: string, password: string): Promise<void> => {
    await registerApi(username, email, password);
    const accessToken = await loginApi(username, password);
    await SecureStore.setItemAsync(TOKEN_KEY, accessToken);
    setToken(accessToken);
  };

  return (
    <AuthContext.Provider value={{ token, isLoading, login, logout, register }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth(): AuthContextType {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used inside <AuthProvider>');
  return ctx;
}
