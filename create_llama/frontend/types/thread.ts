import { DocumentColorEnum } from "@/utils/colors";

export interface Citation {
    documentId: string;
    snippet: string;
    pageNumber: number;
    color: DocumentColorEnum;
  }
  