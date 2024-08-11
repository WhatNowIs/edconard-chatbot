/* eslint-disable @typescript-eslint/no-explicit-any */
import AuthContext from "@/app/context/auth-context";
import ChatContext from "@/app/context/chat-context";
import { getMacroRoundupData } from "@/app/service/user-service";
import {
  Article,
  extractArticleDataFromString,
} from "@/app/utils/multi-mode-select";
import { useGenerateTitle } from "@/app/utils/thread-title-generator";
import React, { useContext, useEffect, useState } from "react";
import { HiArrowSmallUp } from "react-icons/hi2";
import { Button } from "../button";
import FileUploader from "../file-uploader";
import { Input } from "../input";
import UploadImagePreview from "../upload-image-preview";
import { ChatHandler } from "./chat.interface";

export default function ChatInput(
  props: Pick<
    ChatHandler,
    | "isLoading"
    | "input"
    | "onFileUpload"
    | "onFileError"
    | "handleSubmit"
    | "handleInputChange"
  > & {
    multiModal?: boolean;
  },
) {
  const { generateTitle, loading, title } = useGenerateTitle();
  const chatContext = useContext(ChatContext);
  const authContext = useContext(AuthContext);
  const [imageUrl, setImageUrl] = useState<string | null>(null);

  const fetchStream = async (
    data: { role: string; content: string }[],
    input: string,
  ) => {
    const articleData: Article = (await getMacroRoundupData()) as Article;

    const article_data = `
      Headline="${articleData.headline}"
      Authors="${articleData.authors}"
      Summary="${articleData.abstract}"
      Publisher="${articleData.publisher}"
    `;

    const messagesData = [
      ...data,
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
    const response = await fetch("http://54.89.10.40/chat/stream", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Accept: "text/event-stream",
      },
      body: JSON.stringify(messagesData),
    });

    if (!response.ok) {
      console.error("Failed to connect to stream:", response.statusText);
      return;
    }

    const reader: ReadableStreamDefaultReader<Uint8Array> =
      response.body?.getReader() as ReadableStreamDefaultReader<Uint8Array>;
    const decoder = new TextDecoder("utf-8");

    while (true) {
      const { value, done } = await reader.read();
      if (done) {
        break;
      }
      const chunk = decoder.decode(value, { stream: true });
      console.log(chunk); // Handle the chunk (e.g., append to a DOM element)
    }
  };

  const onSubmit = (e: React.FormEvent<HTMLFormElement>) => {
    if (imageUrl) {
      props.handleSubmit(e, {
        data: { imageUrl: imageUrl },
      });
      setImageUrl(null);
      return;
    }
    if (authContext && chatContext) {
      const { user, isResearchExploration } = authContext;
      const { messages, setArticle } = chatContext;

      user &&
        messages.length === 0 &&
        generateTitle(props.input).catch((error) => console.log(error));

      fetchStream(messages, props.input).catch(console.error);

      if (!isResearchExploration) {
        const form = e.currentTarget;
        let inputString = form.elements.namedItem(
          "message",
        ) as HTMLInputElement;

        const currentArticleData = extractArticleDataFromString(
          inputString.value,
        );
        user &&
          messages.length === 0 &&
          generateTitle(props.input).catch((error) => console.log(error));

        if (currentArticleData !== null) {
          setArticle(currentArticleData);
          props.handleSubmit(e);
          return;
        }
      }
    }
    authContext?.isResearchExploration && props.handleSubmit(e);
  };

  const onRemovePreviewImage = () => setImageUrl(null);

  const handleUploadImageFile = async (file: File) => {
    const base64 = await new Promise<string>((resolve, reject) => {
      const reader = new FileReader();
      reader.readAsDataURL(file);
      reader.onload = () => resolve(reader.result as string);
      reader.onerror = (error) => reject(error);
    });
    setImageUrl(base64);
  };

  const handleUploadFile = async (file: File) => {
    try {
      if (props.multiModal && file.type.startsWith("image/")) {
        return await handleUploadImageFile(file);
      }
      props.onFileUpload?.(file);
    } catch (error: any) {
      props.onFileError?.(error.message);
    }
  };

  useEffect(() => {
    if (!loading) {
      if (chatContext && authContext) {
        const { editThread, selectedThread, setSelectedThread } = chatContext;
        const { user } = authContext;
        user &&
          selectedThread &&
          title !== "" &&
          editThread(selectedThread?.id as string, {
            title: title,
            workspace_id: chatContext.currentWorkspace?.id as string,
            user_id: user.id as string,
          });
        user &&
          selectedThread &&
          title !== "" &&
          setSelectedThread({ ...selectedThread, title: title });
      }
    }
  }, [loading]);

  return (
    <form
      onSubmit={onSubmit}
      className="rounded-xl bg-white p-4 space-y-4 mr-4"
    >
      {imageUrl && (
        <UploadImagePreview url={imageUrl} onRemove={onRemovePreviewImage} />
      )}
      <div className="flex w-full items-start justify-between gap-4 ">
        <Input
          autoFocus
          name="message"
          placeholder="Type a message"
          className="flex-1"
          value={props.input}
          onChange={props.handleInputChange}
        />
        <FileUploader
          onFileUpload={handleUploadFile}
          onFileError={props.onFileError}
        />
        <Button type="submit" className="flex gap-1" disabled={props.isLoading}>
          <span>Send </span>
          <HiArrowSmallUp />
        </Button>
      </div>
    </form>
  );
}
