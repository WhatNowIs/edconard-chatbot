import { DocumentColorEnum } from "../utils/colors";

export interface Citation {
  documentId: string;
  snippet: string;
  pageNumber: number;
  ticker: string;
  color: DocumentColorEnum;
}
export interface BackendCitation {
  document_id: string;
  page_number: number;
  score: number;
  text: string;
}
