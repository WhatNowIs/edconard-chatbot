"use client";
/* eslint-disable @typescript-eslint/no-unused-vars */
import { ChatInput, ChatMessages } from "@/app/components/ui/chat";
import AuthContext from "@/app/context/auth-context";
import ChatContext from "@/app/context/chat-context";
import { PdfFocusProvider } from "@/app/context/pdf";
import { Message, useChat } from "ai/react";
import { useContext, useEffect, useState } from "react";
import { ResponseMessage } from "../service/thread-service";
import {
  addChatMessage,
  getCookie,
  getMacroRoundupData,
} from "../service/user-service";
import { Article } from "../utils/multi-mode-select";
import { useGenerateTitle } from "../utils/thread-title-generator";

type ChatUILayout = "default" | "fit";

export default function ChatSection({ layout }: { layout?: ChatUILayout }) {
  const { generateTitle } = useGenerateTitle();
  const authContext = useContext(AuthContext);
  const chatContext = useContext(ChatContext);
  const [accessToken, setAccessToken] = useState<string>("");
  const [isMessageLoading, setIsMessageLoading] = useState<boolean>(false);
  const controller = new AbortController();

  const getChatUrl = () => {
    const isWithinContext = chatContext && authContext;
    if (isWithinContext && authContext?.user && chatContext.selectedThread) {
      return `${process.env.NEXT_PUBLIC_CHAT_API}/${chatContext.selectedThread?.id}/message`;
    }

    return process.env.NEXT_PUBLIC_CHAT_API;
  };

  const {
    messages,
    input,
    isLoading,
    handleSubmit,
    handleInputChange,
    reload,
    stop,
    setMessages,
    setInput,
  } = useChat({
    api: getChatUrl(),
    headers: {
      "Content-Type": "application/json",
      ...(authContext && authContext?.user
        ? { Authorization: `Bearer ${accessToken}` }
        : {}),
    },
    onError: (error) => {
      const message = JSON.parse(error.message);
      alert(`Chat error: ${JSON.stringify(message.detail)}`);
    },
  });

  useEffect(() => {
    if (localStorage) {
      const access_token = localStorage
        ? localStorage.getItem("access_token")
        : getCookie("access_token");
      setAccessToken(access_token as string);
    }
  }, []);

  useEffect(() => {
    if (chatContext) {
      const { messages } = chatContext;
      const finalMessages = messages.map((msg) => ({
        content: msg.content,
        role: msg.role as
          | "system"
          | "user"
          | "assistant"
          | "function"
          | "data"
          | "tool",
        id: msg.id,
        annotations: msg.annotations,
      }));
      setMessages(finalMessages);
    }
  }, [chatContext?.messages]);

  const updateLastMessage = (index: number, newMessage: Partial<Message>) => {
    const updatedMessages = [...messages];
    updatedMessages[messages.length - index] = {
      ...updatedMessages[messages.length - index],
      ...newMessage,
    };

    setMessages(updatedMessages);
  };

  const updateLastMessageStore = (
    index: number,
    newMessage: Partial<ResponseMessage>,
  ) => {
    chatContext?.setMessages((prevMessages) => {
      // Copy the existing
      if (prevMessages.length === 0) return prevMessages;
      const updatedMessages = [...prevMessages];
      updatedMessages[updatedMessages.length - index] = {
        ...updatedMessages[updatedMessages.length - index],
        ...newMessage,
      };

      return updatedMessages;
    });
  };

  async function fetchStream(input: string, thread_id: string) {
    const question = input;
    setIsMessageLoading(true);
    setInput("");

    const newMessages = [
      ...(messages as ResponseMessage[]),
      {
        thread_id: thread_id,
        id: "",
        workspace_id: chatContext?.currentWorkspace?.id as string,
        user_id: authContext?.user?.id as string,
        timestamp: new Date().toISOString(),
        annotations: [],
        role: "user",
        content: question,
      },
      {
        thread_id: thread_id,
        id: "",
        workspace_id: chatContext?.currentWorkspace?.id as string,
        user_id: authContext?.user?.id as string,
        timestamp: new Date().toISOString(),
        annotations: [],
        role: "assistant",
        content: "",
      },
    ];

    const updatedMessages = newMessages.map((msg) => ({
      content: msg.content,
      role: msg.role as
        | "system"
        | "user"
        | "assistant"
        | "function"
        | "data"
        | "tool",
      id: msg.id,
      annotations: msg.annotations,
    }));

    chatContext?.setMessages(newMessages);
    setMessages(updatedMessages);

    const articleData: Article = (await getMacroRoundupData()) as Article;
    const signal = controller.signal;

    const article_data = `
      Headline="${articleData.headline}"
      Author(s)="${articleData.authors}"
      Summary="${articleData.abstract}"
      Publisher="${articleData.publisher}"
    `;

    const cleanedData: { role: string; content: string }[] = messages.map(
      (c: { role: string; content: string }) => {
        return { role: c.role, content: c.content };
      },
    );

    const messagesData = [
      ...cleanedData,
      {
        role: "user",
        content: `
        Here is the article data: ${article_data}\n          
        Question: ${question}
      `,
      },
    ];

    const response = await fetch(
      `${process.env.NEXT_PUBLIC_MODEL_BASE_URL}/chat/stream`,
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Accept: "text/event-stream",
        },
        body: JSON.stringify({ messages: messagesData, streaming: true }),
        signal,
      },
    );

    const reader =
      response.body?.getReader() as ReadableStreamDefaultReader<Uint8Array>;
    const decoder = new TextDecoder("utf-8");

    let result = "";

    while (true) {
      const { value, done } = await reader.read();
      if (done) break;

      const chunk = decoder.decode(value);
      result += chunk;

      updateLastMessage(1, {
        content: result,
      });

      updateLastMessageStore(1, {
        content: result,
      });
    }

    const assistantMessageResponse = (await addChatMessage({
      messages: [
        {
          role: "user",
          content: question,
        },
        {
          role: "assistant",
          content: result,
        },
      ],
      thread_id: thread_id,
    })) as ResponseMessage[];

    assistantMessageResponse
      .reverse()
      .forEach((aiMessage: Partial<ResponseMessage>, index: number) => {
        updateLastMessageStore(index + 1, {
          id: aiMessage.id,
          annotations: aiMessage.annotations,
        });
        updateLastMessage(index + 1, {
          id: aiMessage.id,
          annotations: aiMessage.annotations,
        });
      });

    setIsMessageLoading(false);
  }

  function cancelRequest() {
    controller.abort();

    setIsMessageLoading(false);
  }

  const onSubmit = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    if (authContext && chatContext) {
      const { user, isResearchExploration } = authContext;
      const { selectedThread } = chatContext;

      user &&
        messages.length === 0 &&
        generateTitle(input).catch((error) => console.log(error));

      if (!isResearchExploration) {
        fetchStream(input, selectedThread?.id as string).catch(console.error);
      }
    }
  };

  return (
    <PdfFocusProvider>
      <div
        className={`flex flex-col space-y-4 h-screen overflow-y-auto justify-between w-full pl-4 pb-2`}
      >
        <ChatMessages
          messages={
            authContext?.isResearchExploration
              ? messages
              : (chatContext?.messages as Message[])
          }
          isLoading={
            authContext?.isResearchExploration ? isLoading : isMessageLoading
          }
          reload={reload}
          stop={authContext?.isResearchExploration ? stop : cancelRequest}
        />
        <ChatInput
          input={input}
          handleSubmit={
            authContext?.isResearchExploration ? handleSubmit : onSubmit
          }
          handleInputChange={handleInputChange}
          isLoading={
            authContext?.isResearchExploration ? isLoading : isMessageLoading
          }
          multiModal={true}
        />
      </div>
    </PdfFocusProvider>
  );
}
