import { ChatRequestOptions, Message } from "ai";
import { Dispatch, SetStateAction } from "react";

export interface ChatHandler {
  messages: Message[];
  input: string;
  isLoading: boolean;
  handleSubmit: (e: React.FormEvent<HTMLFormElement>, ops?: ChatRequestOptions) => void;
  handleInputChange: (e: React.ChangeEvent<HTMLInputElement>) => void;
  reload?: () => void;
  stop?: () => void;
  onFileUpload?: (file: File) => Promise<void>;
  onFileError?: (errMsg: string) => void;
  form: any;
  isSubmitting: boolean;
  setIsSubmitting?: Dispatch<SetStateAction<boolean>>;
}
