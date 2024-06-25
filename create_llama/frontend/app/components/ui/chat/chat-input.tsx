/* eslint-disable @typescript-eslint/no-explicit-any */
import React from 'react'; 
import { useContext, useEffect, useState } from "react";
import { Button } from "../button";
import FileUploader from "../file-uploader";
import { Input } from "../input";
import UploadImagePreview from "../upload-image-preview";
import { ChatHandler } from "./chat.interface";
import { useGenerateTitle } from "@/app/utils/thread-title-generator";
import ChatContext from "@/app/context/chat-context";
import AuthContext from "@/app/context/auth-context";

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
      const { user } = authContext;
      const { messages } = chatContext;     
      
      console.log("Clicked messages: ", messages);
      
      user && messages.length === 0 && generateTitle(props.input).catch((error) => console.log(error));
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
        (user && selectedThread) && editThread(selectedThread?.id as string, { title: title, user_id: user.id as string})
        selectedThread && setSelectedThread({...selectedThread, title: title})
      }

    }
  }, [loading]);

  return (
    <form
      onSubmit={onSubmit}
      className="rounded-xl bg-white p-4 shadow-xl space-y-4"
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
        <Button type="submit" disabled={props.isLoading}>
          Send message
        </Button>
      </div>
    </form>
  );
}
