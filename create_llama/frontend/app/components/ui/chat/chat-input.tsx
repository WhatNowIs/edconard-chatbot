/* eslint-disable @typescript-eslint/no-explicit-any */
import React from 'react'; 
import { useContext, useEffect, useState } from "react";
import { Button } from "../button";
import { HiArrowSmallUp } from "react-icons/hi2";
import FileUploader from "../file-uploader";
import { Input } from "../input";
import UploadImagePreview from "../upload-image-preview";
import { ChatHandler } from "./chat.interface";
import { useGenerateTitle } from "@/app/utils/thread-title-generator";
import ChatContext from "@/app/context/chat-context";
import AuthContext from "@/app/context/auth-context";
import { SupportedChatModeEnum, extractArticleDataFromString, convertArticleToString } from '@/app/utils/multi-mode-select';

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

  const onSubmit = (e: React.FormEvent<HTMLFormElement>) => {
    if (imageUrl) {
      props.handleSubmit(e, {
        data: { imageUrl: imageUrl },
      });
      setImageUrl(null);
      return;
    }
    if(authContext && chatContext){
      const { user, chatMode } = authContext;
      const { messages, setArticle } = chatContext;  
      
      user && messages.length === 0 && generateTitle(props.input).catch((error) => console.log(error));

      if(chatMode === SupportedChatModeEnum.MacroRoundupArticleTweetGeneration){
        const form = e.currentTarget;
        let inputString = form.elements.namedItem("message") as HTMLInputElement;
        
        const currentArticleData = extractArticleDataFromString(inputString.value);
        user && messages.length === 0 && generateTitle(props.input).catch((error) => console.log(error));

        if(currentArticleData !== null){
          setArticle(currentArticleData)    
          props.handleSubmit(e);
          return;
        }
      }
    }  
    props.handleSubmit(e);

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
    if(!loading){
      if(chatContext && authContext){
        const { editThread, selectedThread, setSelectedThread } = chatContext;
        const { user } = authContext;
        (user && (selectedThread && title !== "" )) && editThread(selectedThread?.id as string, { title: title, user_id: user.id as string});
        (user && (selectedThread && title !== "" )) && setSelectedThread({...selectedThread, title: title});
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
        <Button type="submit" className='flex gap-1' disabled={props.isLoading}>
          <span>Send </span>
          <HiArrowSmallUp />
        </Button>
      </div>
    </form>
  );
}
