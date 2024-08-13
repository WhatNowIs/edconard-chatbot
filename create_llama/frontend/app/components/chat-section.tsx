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
type Role = "system" | "user" | "assistant" | "function" | "data" | "tool";

export default function ChatSection({ layout }: { layout?: ChatUILayout }) {
  const { generateTitle } = useGenerateTitle();
  const authContext = useContext(AuthContext);
  const chatContext = useContext(ChatContext);
  const [isNonResearchMode, setIsNonResearch] = useState<boolean>(true);
  const [accessToken, setAccessToken] = useState<string>("");
  const [isMessageLoading, setIsMessageLoading] = useState<boolean>(false);
  const controller = new AbortController();
  let question = "";

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
        role: msg.role as Role,
        id: msg.id,
        annotations: msg.annotations,
      }));
      setMessages(finalMessages);
    }
  }, [chatContext?.messages]);

  const updateLastMessage = (index: number, newMessage: Partial<Message>) => {
    setMessages((prevMessages: Message[] = messages) => {
      // Copy the existing
      if (prevMessages?.length === 0) {
        return [newMessage];
      }
      const updatedMessages = [...prevMessages];
      const result = {
        ...updatedMessages[updatedMessages.length - index],
        ...newMessage,
      };
      updatedMessages[updatedMessages.length - index] = result;

      return updatedMessages;
    });
  };

  const updateLastMessageStore = (
    index: number,
    newMessage: Partial<ResponseMessage>,
  ) => {
    chatContext?.setMessages(
      (prevMessages: ResponseMessage[] = chatContext.messages) => {
        // Copy the existing
        if (prevMessages?.length === 0) {
          return [newMessage];
        }
        const updatedMessages = [...prevMessages];
        const result = {
          ...updatedMessages[updatedMessages.length - index],
          ...newMessage,
        };
        updatedMessages[updatedMessages.length - index] = result;

        return updatedMessages;
      },
    );
  };

  function updateMessages(newMessage: ResponseMessage) {
    chatContext?.messages.push(newMessage);
    messages.push({
      role: newMessage.role as Role,
      content: newMessage.content,
      id: "",
      annotations: newMessage.annotations,
    });
  }
  async function processChatMessages(
    reader: ReadableStreamDefaultReader<Uint8Array>,
    thread_id: string,
    question: string,
  ) {
    let result = "";
    setIsMessageLoading(false);
    setIsNonResearch(true);
    updateMessages({
      thread_id: thread_id,
      id: "",
      workspace_id: chatContext?.currentWorkspace?.id as string,
      user_id: authContext?.user?.id as string,
      timestamp: new Date().toISOString(),
      annotations: [],
      role: "assistant",
      content: result,
    });
    const decoder = new TextDecoder();

    while (true) {
      const { value, done } = await reader.read();
      if (done) break;

      const chunk = decoder.decode(value);
      result += chunk;

      updateLastMessageStore(1, {
        content: result,
      });
      updateLastMessage(1, {
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

    updateLastMessageStore(1, {
      id: assistantMessageResponse[1].id,
      annotations: assistantMessageResponse[1].annotations,
    });
    updateLastMessage(1, {
      id: assistantMessageResponse[1].id,
      annotations: assistantMessageResponse[1].annotations,
    });
    console.log("messages - 1: ", messages);
    console.log("chatContext?.messages - 1: ", chatContext?.messages);
  }

  async function fetchStream(input: string, thread_id: string) {
    question = input;
    setIsMessageLoading(true);
    setInput("");

    const articleData: Article = chatContext?.article
      ? chatContext.article
      : ((await getMacroRoundupData()) as Article);
    const signal = controller.signal;

    const cleanedData: { role: string; content: string }[] = messages.map(
      (c: { role: string; content: string }) => {
        return { role: c.role, content: c.content };
      },
    );
    updateMessages({
      thread_id: thread_id,
      id: "",
      workspace_id: chatContext?.currentWorkspace?.id as string,
      user_id: authContext?.user?.id as string,
      timestamp: new Date().toISOString(),
      annotations: [articleData],
      role: "user" as Role,
      content: question,
    });

    const article_data = `
      Headline="${articleData.headline}"
      Author(s)="${articleData.authors}"
      Summary="${articleData.abstract}"
      Publisher="${articleData.publisher}"
    `;

    const messagesData = [
      ...(cleanedData.length > 0 ? cleanedData : []),
      {
        role: "user",
        content: `
        Here is the article data: ${article_data}\n          
        Question: ${question}
      `,
      },
    ];
    console.log("messages: ", messages);
    console.log("chatContext?.messages: ", chatContext?.messages);

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
    processChatMessages(reader, thread_id, question).catch((error) =>
      console.log(error),
    );
    setIsNonResearch(false);
  }

  function cancelRequest() {
    controller.abort();

    setIsMessageLoading(false);
  }

  const onSubmit = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    if (authContext && chatContext) {
      const { user, isResearchExploration } = authContext;
      const { selectedThread, setNonResearchExplorationLLMMessage } =
        chatContext;

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
          messages={messages}
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
