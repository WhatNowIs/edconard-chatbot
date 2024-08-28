"use client";

import {
  ResponseMessage,
  ResponseThread,
  ThreadCreate,
  createThread,
  fetchThreads,
  getMessagesByThreadId,
  getThread,
  removeThread,
  updateThread,
} from "@/app/service/thread-service";
import { Article } from "@/app/utils/multi-mode-select";
import {
  Dispatch,
  FC,
  ReactNode,
  SetStateAction,
  createContext,
  useContext,
  useEffect,
  useState,
} from "react";
import { UserFormType, getMacroRoundupData } from "../service/user-service";
import {
  ResponseWorkspace,
  fetchWorkspaces,
} from "../service/workspace-service";
import { getAccessToken } from "../utils/shared";

export enum SettingPanel {
  Profile = "Profile",
  Accounts = "Accounts",
  // Reports = "Reports",
  Workspace = "Workspaces",
}

interface ChatContextType {
  threads: ResponseThread[];
  messages: ResponseMessage[];
  selectedThread: ResponseThread | null;
  article: Article | null;
  currentSettingPanel: SettingPanel;
  workspaces: ResponseWorkspace[];
  users: UserFormType[];
  workspaceUsers: UserFormType[];
  currentWorkspace: ResponseWorkspace | null;
  selectedWorkspace: ResponseWorkspace | null;
  nonResearchExplorationLLMMessage: string;
  setSelectedThread: Dispatch<SetStateAction<ResponseThread | null>>;
  setThreads: Dispatch<SetStateAction<ResponseThread[]>>;
  loadThreads: (workspaceId: string) => Promise<void>;
  loadWorkspaces: (userId: string) => Promise<void>;
  addThread: (data: ThreadCreate) => Promise<ResponseThread | null>;
  editThread: (
    thread_id: string,
    data: ThreadCreate,
  ) => Promise<ResponseThread | null>;
  fetchThread: (thread_id: string) => Promise<ResponseThread | null>;
  fetchMessages: (thread_id: string) => Promise<ResponseMessage[]>;
  deleteThread: (thread_id: string) => Promise<void>;
  selectThread: (thread_id: string) => void;
  setArticle: Dispatch<SetStateAction<Article | null>>;
  setCurrentSettingPanel: Dispatch<SetStateAction<SettingPanel>>;
  setCurrentWorkspace: Dispatch<SetStateAction<ResponseWorkspace | null>>;
  setSelectedWorkspace: Dispatch<SetStateAction<ResponseWorkspace | null>>;
  setWorkspaces: Dispatch<SetStateAction<ResponseWorkspace[]>>;
  setNonResearchExplorationLLMMessage: Dispatch<SetStateAction<string>>;
  setMessages: Dispatch<SetStateAction<ResponseMessage[]>>;
  setUsers: Dispatch<SetStateAction<UserFormType[]>>;
  setWorkspaceUsers: Dispatch<SetStateAction<UserFormType[]>>;
}

const ChatContext = createContext<ChatContextType | undefined>(undefined);

interface ChatProviderProps {
  children: ReactNode;
}

export const ChatProvider: FC<ChatProviderProps> = ({ children }) => {
  const [threads, setThreads] = useState<ResponseThread[]>([]);
  const [messages, setMessages] = useState<ResponseMessage[]>([]);
  const [selectedThread, setSelectedThread] = useState<ResponseThread | null>(
    null,
  );
  const [workspaces, setWorkspaces] = useState<ResponseWorkspace[]>([]);
  const [users, setUsers] = useState<UserFormType[]>([]);
  const [workspaceUsers, setWorkspaceUsers] = useState<UserFormType[]>([]);
  const [currentWorkspace, setCurrentWorkspace] =
    useState<ResponseWorkspace | null>(null);
  const [selectedWorkspace, setSelectedWorkspace] =
    useState<ResponseWorkspace | null>(null);
  const [currentSettingPanel, setCurrentSettingPanel] = useState<SettingPanel>(
    SettingPanel.Profile,
  );
  const [article, setArticle] = useState<Article | null>(null);
  const [
    nonResearchExplorationLLMMessage,
    setNonResearchExplorationLLMMessage,
  ] = useState<string>("");

  const loadThreads = async (workspaceId: string) => {
    try {
      const fetchedThreads = await fetchThreads(workspaceId);
      setThreads(fetchedThreads);
    } catch (error) {
      console.error("Failed to fetch threads:", error);
    }
  };

  const loadWorkspaces = async () => {
    try {
      const fetchedWorkspaces = await fetchWorkspaces();
      setWorkspaces(fetchedWorkspaces);
    } catch (error) {
      console.error("Failed to fetch threads:", error);
    }
  };

  const fetchMessages = async (thread_id: string) => {
    try {
      const fetchedMessages = await getMessagesByThreadId(thread_id);
      setMessages(fetchedMessages);
      return fetchedMessages;
    } catch (error) {
      console.error("Failed to fetch messages:", error);
      return [];
    }
  };

  const selectThread = async (thread_id: string) => {
    const currentThread = threads.find((thread) => thread.id === thread_id);
    currentThread && setSelectedThread(currentThread);
    await fetchMessages(thread_id);
  };
  const fetchUserWorkspaces = async () => {
    try {
      await loadThreads(currentWorkspace?.id as string);
    } catch (error) {
      console.error("Failed to load threads:", error);
    }
  };

  const fetchUserThreads = async () => {
    try {
      const [_, savedArticle] = await Promise.all([
        loadWorkspaces(),
        getMacroRoundupData(),
      ]);
      if (savedArticle !== null) {
        setArticle(savedArticle as Article);
      }
    } catch (error) {
      console.error("Failed to load threads:", error);
    }
  };

  useEffect(() => {
    const token = getAccessToken();
    if (token && workspaces.length === 0) {
      fetchUserThreads();
    }

    if (token && currentWorkspace && currentWorkspace !== null) {
      fetchUserWorkspaces().catch((error) => console.log(error));
    }
  }, []);

  useEffect(() => {
    const token = getAccessToken();
    if (token && currentWorkspace && currentWorkspace !== null) {
      fetchUserWorkspaces().catch((error) => console.log(error));
    }
  }, [currentWorkspace]);

  useEffect(() => {
    const currentThread = threads[
      threads.length - 1
    ] as unknown as ResponseThread;
    setSelectedThread(currentThread);

    if (currentThread) {
      const loadMessages = async () => {
        await fetchMessages(currentThread.id);
      };
      loadMessages().catch((error) => console.log(error));
    }
  }, [threads]);

  useEffect(() => {
    const currentWS = workspaces[
      workspaces.length - 1
    ] as unknown as ResponseWorkspace;
    setCurrentWorkspace(currentWS);
  }, [workspaces]);

  const addThread = async (data: ThreadCreate) => {
    try {
      const newThread = await createThread(data);
      setThreads([...threads, newThread]);
      return newThread;
    } catch (error) {
      console.error("Failed to create thread:", error);
      return null;
    }
  };

  const editThread = async (thread_id: string, data: ThreadCreate) => {
    try {
      const updatedThread = await updateThread(thread_id, data);
      setThreads(
        threads.map((thread) =>
          thread.id === thread_id ? updatedThread : thread,
        ),
      );
      return updatedThread;
    } catch (error) {
      console.error("Failed to update thread:", error);
      return null;
    }
  };

  const fetchThread = async (thread_id: string) => {
    try {
      const thread = await getThread(thread_id);
      return thread;
    } catch (error) {
      console.error("Failed to fetch thread:", error);
      return null;
    }
  };

  const deleteThread = async (thread_id: string) => {
    try {
      await removeThread(thread_id);
      setThreads(threads.filter((thread) => thread.id !== thread_id));
    } catch (error) {
      console.error("Failed to delete thread:", error);
    }
  };

  return (
    <ChatContext.Provider
      value={{
        threads,
        messages,
        selectedThread,
        article,
        currentSettingPanel,
        workspaces,
        users,
        workspaceUsers,
        currentWorkspace,
        selectedWorkspace,
        nonResearchExplorationLLMMessage,
        setSelectedThread,
        setThreads,
        loadThreads,
        addThread,
        editThread,
        fetchThread,
        fetchMessages,
        deleteThread,
        selectThread,
        setArticle,
        setCurrentSettingPanel,
        setWorkspaces,
        setCurrentWorkspace,
        loadWorkspaces,
        setNonResearchExplorationLLMMessage,
        setMessages,
        setUsers,
        setWorkspaceUsers,
        setSelectedWorkspace,
      }}
    >
      {children}
    </ChatContext.Provider>
  );
};

export const useChat = () => {
  const context = useContext(ChatContext);
  if (!context) {
    throw new Error("useChat must be used within a ChatProvider");
  }
  return context;
};

export default ChatContext;
