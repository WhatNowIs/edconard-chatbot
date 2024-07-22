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
  UserFormType,
  UserSigninType,
  getChatMode,
  getCookie,
  refreshToken,
  signIn,
  signOut,
  updateChatMode,
} from "../service/user-service";
import { getBaseURL } from "../service/utils";

interface AuthContextType {
  user: UserFormType | null;
  chatMode: string | null;
  setChatMode: Dispatch<SetStateAction<string | null>>;
  setUser: Dispatch<SetStateAction<UserFormType | null>>;
  login: (
    credentials: UserSigninType,
  ) => Promise<{ message: string; user: UserFormType | null }>;
  logout: () => Promise<void>;
  getChatModeByUser: (userId: string) => Promise<{ mode: string }>;
  updateChatModeByUser: (
    mode: string,
  ) => Promise<{ message: string; status: number }>;
  refreshAccessToken: () => Promise<string | null | undefined>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider: FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<UserFormType | null>(null);
  const [chatMode, setChatMode] = useState<string | null>(null);

  useEffect(() => {
    const token =
      localStorage.getItem("access_token") || getCookie("access_token");
    if (token && !user) {
      if (!localStorage.getItem("access_token")) {
        localStorage.setItem("access_token", token);
      }

      const checkAuth = async () => {
        const userData = await fetch(`${getBaseURL()}/api/auth/accounts/me`, {
          headers: { Authorization: `Bearer ${token}` },
        })
          .then((response) => {
            return response.json();
          })
          .catch(() => {
            const access_token = refreshAccessToken();

            if (!access_token) {
              localStorage.removeItem("access_token");
              localStorage.removeItem("refresh_token");
              document.cookie = "access_token=; Max-Age=0; path=/;";
              document.cookie = "refresh_token=; Max-Age=0; path=/;";
              setUser(null);
            }
          });

        if (userData) {
          setUser(userData);
          console.log("userData: ", userData);
          // eslint-disable-next-line @typescript-eslint/no-unsafe-member-access
          await getChatModeByUser(userData.id as string);
        }
      };
      checkAuth();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  useEffect(() => {
    if (chatMode === null && user) {
      const fetchChatMode = async () => {
        await getChatModeByUser(user.id as string);
      };
      fetchChatMode();
    }
  }, [user, chatMode]);

  const login = async (credentials: UserSigninType) => {
    try {
      const { access_token, refresh_token, user, message } =
        await signIn(credentials);
      localStorage.setItem("access_token", access_token);
      localStorage.setItem("refresh_token", refresh_token);
      // Set access and refresh token in document's cookie object
      document.cookie = `access_token=${access_token}; path=/;`;
      document.cookie = `refresh_token=${refresh_token}; path=/;`;
      setUser(user);

      return {
        user,
        message,
      };
    } catch (error) {
      return {
        user: null,
        message: "",
      };
    }
  };

  const getChatModeByUser = async (
    userId: string,
  ): Promise<{ mode: string }> => {
    try {
      const token =
        localStorage.getItem("access_token") || getCookie("access_token");

      const { mode } = await getChatMode(userId, token as string);
      setChatMode(mode);
      return {
        mode,
      };
    } catch (error) {
      return {
        mode: "research-or-exploration",
      };
    }
  };

  const refreshAccessToken = async () => {
    try {
      const accessToken = localStorage.getItem("refresh_token");
      const token = accessToken ? accessToken : getCookie("refresh_token");

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
    mode: string,
  ): Promise<{ status: number; message: string }> => {
    try {
      const token =
        localStorage.getItem("access_token") || getCookie("access_token");
      const { message } = await updateChatMode(
        mode,
        user?.id as string,
        token as string,
      );
      setChatMode(mode);

      return {
        status: 200,
        message,
      };
    } catch (error) {
      return {
        status: 400,
        message: `Failed to update chat mode to ${mode}`,
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
        chatMode,
        setChatMode,
        setUser,
        login,
        logout,
        getChatModeByUser,
        updateChatModeByUser,
        refreshAccessToken,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export default AuthContext;
