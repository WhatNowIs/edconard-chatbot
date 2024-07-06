import { Citation } from "@/types/thread";
import { createContext, useContext, useState } from "react";

interface PdfFocusState {
    documentId: string;
    pageNumber: number;
    citation?: Citation;
}
  
interface PdfFocusContextProps {
    pdfFocusState: PdfFocusState;
    setPdfFocusState: React.Dispatch<React.SetStateAction<PdfFocusState>>;
}

interface PdfFocusProviderProps {
    children: React.ReactNode;
}
  // Initialize Context
const PdfFocusContext = createContext<PdfFocusContextProps | undefined>(
    undefined
);

// PDF Provider
export const PdfFocusProvider: React.FC<PdfFocusProviderProps> = ({
    children,
  }) => {
    const [pdfFocusState, setPdfFocusState] = useState<PdfFocusState>({
      documentId: "",
      pageNumber: 0,
    });
  
    return (
      <PdfFocusContext.Provider
        value={{
          pdfFocusState: pdfFocusState,
          setPdfFocusState: setPdfFocusState,
        }}
      >
        {children}
      </PdfFocusContext.Provider>
    );
};
  
// Custom Hook to use PDF Context
export const usePdfFocus = (): PdfFocusContextProps => {
    const context = useContext(PdfFocusContext);
    if (context === undefined) {
      throw new Error("usePDF must be used within a PDFProvider");
    }
    return context;
  };
  
