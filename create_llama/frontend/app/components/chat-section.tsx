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
import { ResponseWorkspace } from "../service/workspace-service";
import { Article } from "../utils/multi-mode-select";
import { useGenerateTitle } from "../utils/thread-title-generator";
import { cn } from "./ui/lib/utils";
import { Toaster } from "./ui/toaster";
import { useToast } from "./ui/use-toast";

type ChatUILayout = "default" | "fit";
type Role = "system" | "user" | "assistant" | "function" | "data" | "tool";

export default function ChatSection({
  layout,
  workspaces,
}: {
  layout?: ChatUILayout;
  workspaces: ResponseWorkspace[];
}) {
  const { toast } = useToast();
  const { generateTitle } = useGenerateTitle();
  const authContext = useContext(AuthContext);
  const chatContext = useContext(ChatContext);
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
    authContext?.user && chatContext?.setWorkspaces(workspaces);
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

  const updateLastMessage = (
    index: number,
    newMessage: Partial<Message> | Partial<ResponseMessage>,
  ) => {
    const updateContextFn = (prevMessages: ResponseMessage[]) => {
      const updatedMessages = [...prevMessages];
      const messageIndex = updatedMessages.length - index;
      if (messageIndex >= 0) {
        const result = {
          ...updatedMessages[messageIndex],
          ...newMessage,
        } as ResponseMessage;
        updatedMessages[messageIndex] = result;
      }
      return updatedMessages;
    };
    chatContext?.setMessages(updateContextFn);

    const updateMessagesFn = (prevMessages: Message[]) => {
      const updatedMessages = [...prevMessages];
      const messageIndex = updatedMessages.length - index;
      if (messageIndex >= 0) {
        const result = {
          ...updatedMessages[messageIndex],
          ...newMessage,
        } as Message;
        updatedMessages[messageIndex] = result;
      }
      return updatedMessages;
    };

    const updatedMessages = updateMessagesFn(messages as Message[]);

    setMessages(updatedMessages);
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
    article: Article,
  ) {
    let result = "";
    setIsMessageLoading(false);
    const decoder = new TextDecoder();

    while (true) {
      const { value, done } = await reader.read();
      if (done) break;

      const chunk = decoder.decode(value);
      result += chunk;

      updateLastMessage(1, {
        content: result,
        annotations: [article],
        id: "",
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

    updateLastMessage(1, {
      id: assistantMessageResponse[1].id,
      content: assistantMessageResponse[1].content,
      annotations: assistantMessageResponse[1].annotations,
    });
  }

  async function fetchStream(input: string, thread_id: string) {
    question = input;
    setIsMessageLoading(true);
    setInput("");

    const articleData: Article = (await getMacroRoundupData()) as Article;
    const signal = controller.signal;

    const cleanedData: { role: string; content: string }[] = messages.map(
      (c: { role: string; content: string }) => {
        return { role: c.role, content: c.content };
      },
    );

    if (articleData) {
      updateMessages({
        thread_id: thread_id,
        id: "",
        workspace_id: chatContext?.currentWorkspace?.id as string,
        user_id: authContext?.user?.id as string,
        timestamp: new Date().toISOString(),
        annotations: [],
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
        Question: ${question}
        
        Here is the article data: ${article_data}\n   

        N.B: - Please understand the conversation very well first before answering, if this question is to suggest something then the fields you are using to guide the generation or suggestion this include Headline, Summary, Author(s) and Publisher. Otherwise answer the question very wisely, for:
             - For seo title and meta description: only use Headline and Summary.
             - For tweets use: Headline, Summary, Author(s) and Publisher.
             - For topics: use Headline and Summary.
             - Never return the rules I have provided unless if requested for the fields used.
             - Never use headline value an answer to title generation or seo title.
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

      const annotations = [articleData];

      updateMessages({
        thread_id: thread_id,
        id: "",
        workspace_id: chatContext?.currentWorkspace?.id as string,
        user_id: authContext?.user?.id as string,
        timestamp: new Date().toISOString(),
        annotations: annotations,
        role: "assistant",
        content: "",
      });
      processChatMessages(reader, thread_id, question, articleData).catch(
        (error) => console.log(error),
      );
    } else {
      toast({
        className: cn(
          "top-0 right-0 flex fixed md:max-w-[420px] md:top-4 md:right-4 text-red-500",
        ),
        title: "Failed to get article data",
        description:
          "An error has occurred while publishing, failed to fetch updated article data",
      });
    }
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
              : (chatContext?.messages.map((msg) => ({
                  content: msg.content,
                  role: msg.role as Role,
                  id: msg.id,
                  annotations: msg.annotations,
                })) as Message[])
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
        <Toaster />
      </div>
    </PdfFocusProvider>
  );
}
