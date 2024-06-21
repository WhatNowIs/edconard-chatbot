"use client";

import { createContext, useState, ReactNode, FC, useContext, useEffect } from 'react';
import { ResponseMessage, ResponseThread, ThreadCreate, createThread, fetchThreads, getMessagesByThreadId, getThread, removeThread, updateThread } from '../service/thread-service';

interface ChatContextType {
  threads: ResponseThread[];
  messages: ResponseMessage[];
  selectedThread: ResponseThread | null;
  loadThreads: () => Promise<void>;
  addThread: (data: ThreadCreate) => Promise<ResponseThread | null>;
  editThread: (thread_id: string, data: ThreadCreate) => Promise<ResponseThread | null>;
  fetchThread: (thread_id: string) => Promise<ResponseThread | null>;
  fetchMessages: (thread_id: string) => Promise<ResponseMessage[]>;
  deleteThread: (thread_id: string) => Promise<void>;
  selectThread: (thread_id: string) => void;
}

const ChatContext = createContext<ChatContextType | undefined>(undefined);

interface ChatProviderProps {
  children: ReactNode;
}

export const ChatProvider: FC<ChatProviderProps> = ({ children }) => {
  const [threads, setThreads] = useState<ResponseThread[]>([]);
  const [messages, setMessages] = useState<ResponseMessage[]>([]);
  const [selectedThread, setSelectedThread] = useState<ResponseThread | null>(null);

  const loadThreads = async () => {
    try {
      const fetchedThreads = await fetchThreads();
      setThreads(fetchedThreads);
    } catch (error) {
      console.error('Failed to fetch threads:', error);
    }
  };
  
  const fetchMessages = async (thread_id: string) => {
    try {
      const fetchedMessages = await getMessagesByThreadId(thread_id);
      setMessages(fetchedMessages);
      return fetchedMessages;
    } catch (error) {
      console.error('Failed to fetch messages:', error);
      return [];
    }
  };

  const selectThread = async (thread_id: string) => {
    const currentThread = threads.find((thread) => thread.id === thread_id);
    currentThread && setSelectedThread(currentThread);
    await fetchMessages(thread_id)
  }

  useEffect(() => {
    const token = localStorage.getItem('access_token');
    if (token) {
      const fetchUserThreads = async () => {
        try {
          await loadThreads();
        } catch (error) {
          console.error('Failed to load threads:', error);
        }
      };

      fetchUserThreads();
    }
  }, []);

  
  useEffect(() => {
    setSelectedThread(threads[threads.length - 1] as unknown as ResponseThread);    
  }, [threads]);

  const addThread = async (data: ThreadCreate) => {
    try {
      const newThread = await createThread(data);
      setThreads([...threads, newThread]);
      return newThread;
    } catch (error) {
      console.error('Failed to create thread:', error);
      return null;
    }
  };

  const editThread = async (thread_id: string, data: ThreadCreate) => {
    try {
      const updatedThread = await updateThread(thread_id, data);
      setThreads(threads.map(thread => (thread.id === thread_id ? updatedThread : thread)));
      return updatedThread;
    } catch (error) {
      console.error('Failed to update thread:', error);
      return null;
    }
  };

  const fetchThread = async (thread_id: string) => {
    try {
      const thread = await getThread(thread_id);
      return thread;
    } catch (error) {
      console.error('Failed to fetch thread:', error);
      return null;
    }
  };

  const deleteThread = async (thread_id: string) => {
    try {
      await removeThread(thread_id);
      setThreads(threads.filter(thread => thread.id !== thread_id));
    } catch (error) {
      console.error('Failed to delete thread:', error);
    }
  };

  return (
    <ChatContext.Provider
      value={{
        threads,
        messages,
        selectedThread,
        loadThreads,
        addThread,
        editThread,
        fetchThread,
        fetchMessages,
        deleteThread,
        selectThread
      }}
    >
      {children}
    </ChatContext.Provider>
  );
};

export const useChat = () => {
  const context = useContext(ChatContext);
  if (!context) {
    throw new Error('useChat must be used within a ChatProvider');
  }
  return context;
};

export default ChatContext;
