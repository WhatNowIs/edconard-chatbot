"use client";
/* eslint-disable @typescript-eslint/no-unused-vars */
import React from 'react';
import { useChat } from "ai/react";
import { ChatInput, ChatMessages } from "@/app/components/ui/chat";
import { PdfFocusProvider } from "@/app/context/pdf";
import { useContext, useEffect, useState } from "react";
import AuthContext from "@/app/context/auth-context";
import ChatContext from "@/app/context/chat-context";

type ChatUILayout = "default" | "fit";

export default function ChatSection({ layout }: { layout?: ChatUILayout }) {
  const authContext = useContext(AuthContext);
  const chatContext = useContext(ChatContext);
  const [accessToken, setAccessToken] = useState<string>('');
  
  const getChatUrl = () => {
    const isWithinContext = (chatContext && authContext)
    if(isWithinContext && authContext?.user && chatContext.selectedThread){
      return `${process.env.NEXT_PUBLIC_CHAT_API}/${chatContext.selectedThread?.id}/message`;
    }

    return process.env.NEXT_PUBLIC_CHAT_API
  }

  const {
    messages,
    input,
    isLoading,
    handleSubmit,
    handleInputChange,
    reload,
    stop,
    setMessages
  } = useChat({
    api: getChatUrl(),
    headers: {
      "Content-Type": "application/json",
      ...(authContext && authContext?.user ? { Authorization: `Bearer ${accessToken}` } : {}),
    },
    onError: (error) => {
      const message = JSON.parse(error.message);
      alert(`Chat error: ${JSON.stringify(message.detail)}`);
    },
  });  

  useEffect(() => {
    if(localStorage){      
      const access_token = localStorage ? localStorage.getItem('access_token') : null;
      setAccessToken(access_token as string);
    }

  }, []);

  useEffect(() => {
    if(chatContext){
      const { messages } = chatContext;
      const finalMessages =  messages.map((msg) => ({ 
        content: msg.content, 
        role: msg.role as ('system' | 'user' | 'assistant' | 'function' | 'data' | 'tool'), 
        id: msg.id,
        annotations: msg.annotations
      }));
      setMessages(finalMessages)
    }

  }, [chatContext?.messages]);

  return (
    <PdfFocusProvider>
      <div
        className={`flex flex-col space-y-4 h-screen overflow-y-auto justify-between w-full pl-4 pb-2`}
      >
        <ChatMessages
          messages={messages}
          isLoading={isLoading}
          reload={reload}
          stop={stop}
        />
        <ChatInput
          input={input}
          handleSubmit={handleSubmit}
          handleInputChange={handleInputChange}
          isLoading={isLoading}
          multiModal={true}
        />
      </div>
    </PdfFocusProvider>
  );
}
