/* eslint-disable @typescript-eslint/no-unsafe-assignment */
"use client";
/* eslint-disable no-useless-catch */
import {
  Dispatch,
  FC,
  ReactNode,
  SetStateAction,
  createContext,
  useEffect,
  useState,
} from "react";
import {
  SignInResponse,
  UserFormType,
  UserSigninType,
  getChatMode,
  getCookie,
  getMe,
  refreshToken,
  signIn,
  signOut,
  updateChatMode,
} from "../service/user-service";
import { getAccessToken } from "../utils/shared";

interface AuthContextType {
  user: UserFormType | null;
  currentUser: UserFormType | null;
  users: UserFormType[];
  isResearchExploration: boolean | null;
  setIsResearchExploration: Dispatch<SetStateAction<boolean | null>>;
  setUser: Dispatch<SetStateAction<UserFormType | null>>;
  setUsers: Dispatch<SetStateAction<UserFormType[]>>;
  login: (
    credentials: UserSigninType,
  ) => Promise<{ message: string; user: UserFormType | null }>;
  logout: () => Promise<void>;
  getChatModeByUser: (userId: string) => Promise<{ mode: boolean }>;
  updateChatModeByUser: (
    checked: boolean,
  ) => Promise<{ message: string; status: number }>;
  setCurrentUser: Dispatch<SetStateAction<UserFormType | null>>;
  refreshAccessToken: () => Promise<string | null | undefined>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider: FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<UserFormType | null>(null);
  const [currentUser, setCurrentUser] = useState<UserFormType | null>(null);
  const [users, setUsers] = useState<UserFormType[]>([]);
  const [isResearchExploration, setIsResearchExploration] = useState<
    boolean | null
  >(null);

  useEffect(() => {
    const token = getAccessToken();
    if (token && user === null) {
      if (!localStorage.getItem("access_token")) {
        localStorage.setItem("access_token", token);
      }

      const checkAuth = async () => {
        const response = await getMe(token);

        if (response.data !== null) {
          console.log("userData: ", response.data);
          setUser(response.data);
          const { mode } = await getChatModeByUser(response.data.id as string);
          setIsResearchExploration(mode);
        }
      };
      checkAuth();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  useEffect(() => {
    if (isResearchExploration === null && user) {
      const fetchChatMode = async () => {
        await getChatModeByUser(user.id as string);
      };
      fetchChatMode();
    }
  }, [user, isResearchExploration]);

  const login = async (credentials: UserSigninType) => {
    try {
      const { message, user, ...result } = await signIn(credentials);

      if (user !== null) {
        const { access_token, refresh_token } = result as SignInResponse;
        localStorage.setItem("access_token", access_token);
        localStorage.setItem("refresh_token", refresh_token);
        // Set access and refresh token in document's cookie object
        document.cookie = `access_token=${access_token}; path=/;`;
        document.cookie = `refresh_token=${refresh_token}; path=/;`;
        setUser(user);
      }

      return {
        user,
        message,
      };
    } catch (error: any) {
      return {
        user: null,
        message: "An error has occurred while trying to login",
      };
    }
  };

  const getChatModeByUser = async (
    userId: string,
  ): Promise<{ mode: boolean }> => {
    try {
      const token = getAccessToken();

      const { mode } = await getChatMode(userId, token as string);
      console.log(`got chat mode: ${mode}`);
      setIsResearchExploration(mode);
      console.log(`got chat mode - 1: ${isResearchExploration}`);
      return {
        mode,
      };
    } catch (error) {
      return {
        mode: true,
      };
    }
  };

  const refreshAccessToken = async () => {
    try {
      const token = getAccessToken();

      const { access_token } = await refreshToken(token as string);

      if (access_token) {
        localStorage.setItem("access_token", access_token);
        document.cookie = `access_token=${access_token}; path=/;`;
      }
      return access_token;
    } catch (error) {
      console.error(error);
    }
  };

  const updateChatModeByUser = async (
    checked: boolean,
  ): Promise<{ status: number; message: string }> => {
    try {
      console.log(`Update chat mode to: ${checked}`);
      const token =
        localStorage.getItem("access_token") || getCookie("access_token");
      const { message } = await updateChatMode(
        checked,
        user?.id as string,
        token as string,
      );
      setIsResearchExploration(checked);

      return {
        status: 200,
        message,
      };
    } catch (error) {
      return {
        status: 400,
        message: `Failed to update chat mode to ${checked}`,
      };
    }
  };

  const logout = async () => {
    try {
      const access_token =
        localStorage.getItem("access_token") || getCookie("access_token");
      const refresh_token =
        localStorage.getItem("refresh_token") || getCookie("refresh_token");
      if (access_token || refresh_token) {
        await signOut(access_token as string);

        localStorage.removeItem("access_token");
        localStorage.removeItem("refresh_token");
        // Remove access and refresh token in document's cookie object
        document.cookie = "access_token=; Max-Age=0; path=/;";
        document.cookie = "refresh_token=; Max-Age=0; path=/;";
        setUser(null);
      }
    } catch (error) {
      throw error;
    }
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        currentUser,
        users,
        isResearchExploration,
        setIsResearchExploration,
        setUser,
        login,
        logout,
        getChatModeByUser,
        updateChatModeByUser,
        refreshAccessToken,
        setUsers,
        setCurrentUser,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export default AuthContext;
