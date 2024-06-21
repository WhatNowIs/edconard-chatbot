"use client";

import { useChat } from "ai/react";
import { ChatInput, ChatMessages } from "./ui/chat";
import { PdfFocusProvider } from "@/app/context/pdf";
import { useContext, useEffect } from "react";
import AuthContext from "../context/auth-context";
import ChatContext from "../context/chat-context";

type ChatUILayout = "default" | "fit";

export default function ChatSection({ layout }: { layout?: ChatUILayout }) {
  const authContext = useContext(AuthContext);
  const chatContext = useContext(ChatContext);
  const access_token = localStorage.getItem('access_token');
  
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
      ...(authContext && authContext?.user ? { Authorization: `Bearer ${access_token}` } : {}),
    },
    onError: (error) => {
      const message = JSON.parse(error.message);
      alert(`Chat error: ${JSON.stringify(message.detail)}`);
    },
  });

  

  useEffect(() => {

    console.log('Old messages: ');
    console.log(messages)

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
        className={`flex flex-col space-y-4 justify-between w-full p-4`}
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
