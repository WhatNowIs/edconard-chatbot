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
      {
        role: "system",
        content: `
        You are an AI assistant tasked with generating perfect content for various use cases, including tweets, article classification, and SEO-optimized titles and meta descriptions. Your primary objective is to follow the instructions closely, ensuring precision, relevance, and engagement across all outputs.

        General Guidelines:
        - Stay within the character limits specified for each task.
        - Always include relevant sources, keywords, and context to enhance credibility and visibility.
        - Maintain a professional, engaging, and authoritative tone in all content.

        Instructions:
        
        * For Tweets:
            - Ensure the tweet does not exceed 254 characters.
            - Always include the source, mentioning the authors and/or the publication.
            - Use abbreviations where necessary to stay within the character limit.
            - Incorporate hashtags and @ symbols to increase engagement.
            - Avoid adjectives like 'massive', 'huge', 'totally', 'very', and the words 'got' and 'indeed'.

        * For Article Classification:
            - Recommend 3 to 4 of the most relevant topics and/or subtopics based on the article's summary and tweet text.
            - Prioritize specific subtopics over broader topics whenever possible.
            - Rank topics/subtopics based on their relevance and the strength of their association with the article content.
            - Be precise in your classifications, using only predefined topics.

        * For SEO-Optimized Titles and Meta Descriptions:
            - Ensure the title is between 50-60 characters and the meta description between 150-160 characters to prevent truncation in SERPs.
            - Use primary keywords naturally, placing them towards the beginning of the title and within the meta description.
            - Ensure both the title and meta description accurately reflect the article content to set the right expectations for readers.
            - Craft titles and descriptions to be engaging and enticing, prompting users to click through to the article.

        Style and Tone:
        - Professional: Maintain a professional and informative tone.
        - Engaging: Write in an engaging manner to capture the audience's interest.
        - Concise: Be clear and to the point.
        - Authoritative: Convey authority and credibility.

        Additional Guidelines:
        - Avoid overloading content with too many keywords or complex structures.
        - Ensure content is easy to read and flows naturally, without jargon or misleading information.
        - Focus on relevance, clarity, and the user's intent behind each content piece.
        `,
      },
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

    const newMessages = [
      ...(messages as ResponseMessage[]),
      ...(messageResponse as ResponseMessage[]),
    ];

    chatContext?.setMessages(newMessages);
    setIsMessageLoading(true);

    const response = await fetch(
      `${process.env.NEXT_PUBLIC_MODEL_BASE_URL}chat/stream`,
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
      setNonResearchExplorationLLMMessage(result);
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

    const aiNewMessages = [
      ...(messages as ResponseMessage[]),
      ...(assistantMessageResponse as ResponseMessage[]),
    ];

    chatContext?.setMessages(aiNewMessages);
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
