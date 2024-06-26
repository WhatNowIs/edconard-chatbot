"use client"
/* eslint-disable no-useless-catch */

import React from 'react'; 
import { createContext, useState, useEffect, ReactNode, FC, Dispatch, SetStateAction } from 'react';
import { getBaseURL } from '../service/utils';
import { UserFormType, UserSigninType, getChatMode, signIn, signOut, updateChatMode } from '../service/user-service';

interface AuthContextType {
    user: UserFormType | null;
    chatMode: string | null;
    setChatMode: Dispatch<SetStateAction<string | null>>;
    setUser: Dispatch<SetStateAction<UserFormType | null>>;
    login: (credentials: UserSigninType) => Promise<{ message: string; user: UserFormType | null; }>;
    logout: () => Promise<void>;
    getChatModeByUser: (userId: string) => Promise<{mode: string}>;
    updateChatModeByUser: (mode: string) => Promise<{ message: string; status: number; }>;
}
  
const AuthContext = createContext<AuthContextType | undefined>(undefined);

interface AuthProviderProps {
    children: ReactNode;
}

export const AuthProvider: FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<UserFormType | null>(null);
  const [chatMode, setChatMode] = useState<string | null>(null);

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

  useEffect(() => {    
    if(chatMode === null && user){
      const fetchChatMode = async () => {
        await getChatModeByUser(user.id as string);
      };
      fetchChatMode();
    }
  }, [user, chatMode])

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

  const getChatModeByUser = async (userId: string): Promise<{mode: string}> => {
    try {
      const token = localStorage.getItem('access_token');
      const { mode } = await getChatMode(userId, token as string);
      setChatMode(mode);
      return {
        mode
      }
    } catch (error) {
        return {
            mode: "research-or-exploration",
        }
    }
  };
  

  const updateChatModeByUser = async (mode: string): Promise<{status: number; message: string}> => {
    try {
      const token = localStorage.getItem('access_token');
      const { message } = await updateChatMode(mode, user?.id as string, token as string);
      setChatMode(mode);

      return {
        status: 200,
        message
      }
    } catch (error) {
        return {
          status: 400,
          message: `Failed to update chat mode to ${mode}`,
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
    <AuthContext.Provider value={{ user, chatMode, setChatMode, setUser, login, logout, getChatModeByUser, updateChatModeByUser }}>
      {children}
    </AuthContext.Provider>
  );
};

export default AuthContext;
