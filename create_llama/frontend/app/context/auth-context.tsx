"use client"

import { createContext, useState, useEffect, ReactNode, FC } from 'react';
import { getBaseURL } from '../service/utils';
import { UserFormType, UserSigninType, signIn, signOut } from '../service/user-service';

interface AuthContextType {
    user: UserFormType | null;
    login: (credentials: UserSigninType) => Promise<{ message: string; user: UserFormType | null; }>;
    logout: () => Promise<void>;
}
  
const AuthContext = createContext<AuthContextType | undefined>(undefined);

interface AuthProviderProps {
    children: ReactNode;
}

export const AuthProvider: FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<UserFormType | null>(null);
  // const [threads, setThreads] = useState<UserFormType | null>(null);

  useEffect(() => {
    const token = localStorage.getItem('access_token');
    if (token) {
      const checkAuth = async () => {
        try {
          const response = await fetch(`${getBaseURL()}/api/auth/accounts/me`, {
            headers: { Authorization: `Bearer ${token}` },
          });
          const userData = await response.json();

          console.log("checkAuth: ", userData);

          setUser(userData);
        } catch (error) {
          localStorage.removeItem('access_token');
          setUser(null);
        }
      };
      checkAuth();
    }
    console.log("token: ", token);
  }, []);

  const login = async (credentials: UserSigninType) => {
    try {
      const { access_token, user, message } = await signIn(credentials);
      localStorage.setItem('access_token', access_token);

      console.log("Login: ", user)
      setUser(user);

      return {
        user, message
      }
    } catch (error) {
        return {
            user: null,
            message: ""
        }
    }

  };

  const logout = async () => {
    try {
      const token = localStorage.getItem('access_token');
      if(token){
        await signOut(token as string);
        localStorage.removeItem('access_token');
        setUser(null);
      }
    } catch (error) {
      throw error;
    }
  };

  return (
    <AuthContext.Provider value={{ user, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
};

export default AuthContext;
