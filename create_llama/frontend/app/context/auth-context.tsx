"use client"
/* eslint-disable no-useless-catch */

import React from 'react'; 
import { createContext, useState, useEffect, ReactNode, FC, Dispatch, SetStateAction } from 'react';
import { getBaseURL } from '../service/utils';
import { UserFormType, UserSigninType, getChatMode, signIn, signOut, updateChatMode } from '../service/user-service';

interface AuthContextType {
    user: UserFormType | null;
    isResearchExploration: boolean | null;
    setIsResearchExploration: Dispatch<SetStateAction<boolean | null>>;
    setUser: Dispatch<SetStateAction<UserFormType | null>>;
    login: (credentials: UserSigninType) => Promise<{ message: string; user: UserFormType | null; }>;
    logout: () => Promise<void>;
    getChatModeByUser: (userId: string) => Promise<{mode: boolean}>;
    updateChatModeByUser: (checked: boolean) => Promise<{ message: string; status: number; }>;
}
  
const AuthContext = createContext<AuthContextType | undefined>(undefined);

interface AuthProviderProps {
    children: ReactNode;
}

export const AuthProvider: FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<UserFormType | null>(null);
  const [isResearchExploration, setIsResearchExploration] = useState<boolean | null>(true);

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
    if(isResearchExploration === null && user){
      const fetchChatMode = async () => {
        await getChatModeByUser(user.id as string);
      };
      fetchChatMode();
    }
  }, [user, isResearchExploration])

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

  const getChatModeByUser = async (userId: string): Promise<{mode: boolean}> => {
    try {
      const token = localStorage.getItem('access_token');
      const { mode } = await getChatMode(userId, token as string);
      setIsResearchExploration(mode);
      return {
        mode
      }
    } catch (error) {
        return {
            mode: true,
        }
    }
  };
  

  const updateChatModeByUser = async (checked: boolean): Promise<{status: number; message: string}> => {
    try {
      const token = localStorage.getItem('access_token');
      const { message } = await updateChatMode(checked, user?.id as string, token as string);
      setIsResearchExploration(checked);

      return {
        status: 200,
        message
      }
    } catch (error) {
        return {
          status: 400,
          message: `Failed to update chat mode to ${checked}`,
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
    <AuthContext.Provider value={{ user, isResearchExploration, setIsResearchExploration, setUser, login, logout, getChatModeByUser, updateChatModeByUser }}>
      {children}
    </AuthContext.Provider>
  );
};

export default AuthContext;
