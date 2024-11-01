/* eslint-disable @typescript-eslint/no-explicit-any */
import AuthContext from "@/app/context/auth-context";
import ChatContext from "@/app/context/chat-context";
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

  const onSubmit = (e: React.FormEvent<HTMLFormElement>) => {
    if (imageUrl) {
      props.handleSubmit(e, {
        data: { imageUrl: imageUrl },
      });
      setImageUrl(null);
      return;
    }

    if (authContext && chatContext) {
      const { user } = authContext;
      const { messages } = chatContext;

      user &&
        messages.length === 0 &&
        generateTitle(props.input).catch((error) => console.log(error));
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
        {authContext?.isResearchExploration && (
          <FileUploader
            onFileUpload={handleUploadFile}
            onFileError={props.onFileError}
          />
        )}
        <Button type="submit" className="flex gap-1" disabled={props.isLoading}>
          <span>Send </span>
          <HiArrowSmallUp />
        </Button>
      </div>
    </form>
  );
}
