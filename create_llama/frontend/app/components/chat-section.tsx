"use client";
/* eslint-disable @typescript-eslint/no-unused-vars */
import { ChatInput, ChatMessages } from "@/app/components/ui/chat";
import AuthContext from "@/app/context/auth-context";
import ChatContext from "@/app/context/chat-context";
import { PdfFocusProvider } from "@/app/context/pdf";
import { useChat } from "ai/react";
import {
  Dispatch,
  SetStateAction,
  useContext,
  useEffect,
  useState,
} from "react";
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

  async function fetchStream(
    data: { role: string; content: string }[],
    input: string,
    thread_id: string,
    setNonResearchExplorationLLMMessage: Dispatch<SetStateAction<string>>,
  ) {
    setIsMessageLoading(true);
    const articleData: Article = (await getMacroRoundupData()) as Article;
    const signal = controller.signal;

    const article_data = `
      Headline="${articleData.headline}"
      Authors="${articleData.authors}"
      Summary="${articleData.abstract}"
      Publisher="${articleData.publisher}"
    `;

    const cleanedData: { role: string; content: string }[] = data.map(
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
          
        Here are all the predefined topics and subtopics, do not return anything which is not listed here:     
        "1. Comparisons:
            - Age
            - Cross-country
            - Gender
            - Geography (Urban/Rural)
            - Historical
            - Liberal/Conservative
            - No Comparison
            - Other Comparison
            - Race
            - Sector
            - Skill Level
        
        2. Fiscal Policy:
            - Fiscal Deficits
            - Government Spending
            - Infrastructure
            - Multiplier/Rational Expectations
            - Regulation
            - Taxation
        
        3. GDP:
            - Business Cycle
            - Financial Markets
            - Growth
            - Housing
            - Inflation
            - Savings Glut/Trade Deficit
            - Trade (not deficits)
        
        4. Monetary Policy:
            - Banking
            - Financial Crisis
            - M&M
        
        5. Science:
            - Cosmos
            - Evolution/Heredity
            - Fraudulent Studies
            - Global Warming
            - Other Science
        
        6. Workforce:
            - Demographics
            - Education
            - Family/Marriage
            - Gender Pay Gap
            - Immigration
            - Inequality
            - Minimum Wage
            - Mobility/Assortive Mating
            - Poverty/Crime
            - Unemployment/Participation
            - Wages/Income
            - Workforce Reorganization/Participation
        
        7. Productivity:
            - Cronyism
            - Incentives/Risk-Taking
            - Innovation/Research
            - Institutional Capabilities
            - Intangibles
            - Investment
            - Startups
            - Workforce Reorganization/Participation
        
        8. Energy"
        Question: ${input}
      `,
      },
    ];

    const messageResponse = await addChatMessage({
      messages: [
        {
          role: "user",
          content: input,
        },
      ],
      thread_id: thread_id,
    });

    chatContext?.setMessages([
      ...(chatContext?.messages as ResponseMessage[]),
      ...(messageResponse as ResponseMessage[]),
    ]);

    const response = await fetch("http://54.89.10.40/chat/stream", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Accept: "text/event-stream",
      },
      body: JSON.stringify({ messages: messagesData, streaming: true }),
      signal,
    });
    const reader =
      response.body?.getReader() as ReadableStreamDefaultReader<Uint8Array>;
    const decoder = new TextDecoder("utf-8");

    let result = "";

    while (true) {
      const { value, done } = await reader.read();
      if (done) break;

      const chunk = decoder.decode(value);
      result += chunk;

      setNonResearchExplorationLLMMessage((result += chunk));
    }

    const assistantMessageResponse = await addChatMessage({
      messages: [
        {
          role: "assistant",
          content: result,
        },
      ],
      thread_id: thread_id,
    });
    chatContext?.setMessages([
      ...(chatContext?.messages as ResponseMessage[]),
      ...(assistantMessageResponse as ResponseMessage[]),
    ]);
    setIsMessageLoading(false);
  }

  function cancelRequest() {
    controller.abort();

    setIsMessageLoading(false);
  }

  const onSubmit = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    console.log(
      `authContext?.isResearchExploration: ${authContext?.isResearchExploration}`,
    );
    if (authContext && chatContext) {
      const { user, isResearchExploration } = authContext;
      const { messages, setNonResearchExplorationLLMMessage, selectedThread } =
        chatContext;

      user &&
        messages.length === 0 &&
        generateTitle(input).catch((error) => console.log(error));

      if (!isResearchExploration) {
        fetchStream(
          messages,
          input,
          selectedThread?.id as string,
          setNonResearchExplorationLLMMessage,
        ).catch(console.error);
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
