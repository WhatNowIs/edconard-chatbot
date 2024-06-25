"use client"
/* eslint-disable no-useless-catch */

import React from 'react'; 
import { createContext, useState, useEffect, ReactNode, FC, Dispatch, SetStateAction } from 'react';
import { getBaseURL } from '../service/utils';
import { UserFormType, UserSigninType, signIn, signOut } from '../service/user-service';

interface AuthContextType {
    user: UserFormType | null;
    setUser: Dispatch<SetStateAction<UserFormType | null>>;
    login: (credentials: UserSigninType) => Promise<{ message: string; user: UserFormType | null; }>;
    logout: () => Promise<void>;
}
  
const AuthContext = createContext<AuthContextType | undefined>(undefined);

interface AuthProviderProps {
    children: ReactNode;
}

export const AuthProvider: FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<UserFormType | null>(null);

  useEffect(() => {
    const token = localStorage.getItem('access_token');
    if (token && !user) {
      const checkAuth = async () => {
          const userData = await fetch(`${getBaseURL()}/api/auth/accounts/me`, {
            headers: { Authorization: `Bearer ${token}` },
          })
          .then(response => {
            return response.json();
          })
          .catch(() => {
            localStorage.removeItem('access_token');
            setUser(null);
          });
          setUser(userData);
      };
      checkAuth();
    }
  }, []);

  const login = async (credentials: UserSigninType) => {
    try {
      const { access_token, user, message } = await signIn(credentials);
      localStorage.setItem('access_token', access_token);
      document.cookie = `access_token=${access_token}; path=/;`;
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
        document.cookie = 'access_token=; Max-Age=0; path=/;';
        setUser(null);
      }
    } catch (error) {
      throw error;
    }
  };

  return (
    <AuthContext.Provider value={{ user, setUser, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
};

export default AuthContext;
