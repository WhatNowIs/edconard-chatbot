import { usePdfFocus } from "@/app/context/pdf";
import { Citation } from "@/app/types/threads";
import { borderColors } from "@/app/utils/colors";
import PdfDialog from "./PdfDialog";
import { getStaticFileDataUrl } from "../../lib/url";

import { SourceNode } from "@/app/components/ui/chat";

interface CitationDisplayProps {
  citation: Citation;
  source: SourceNode;
}

const CitationDisplay: React.FC<CitationDisplayProps> = ({ citation, source}) => {
  const { setPdfFocusState } = usePdfFocus();
  const handleCitationClick = (documentId: string, pageNumber: number) => {
    setPdfFocusState({ documentId, pageNumber, citation });
    console.log(`Clicked Page Number ${pageNumber}`);
  };

  const CitationNode = () => {
    return (
      <div
      className={`mx-1.5 mb-2 min-h-[25px] min-w-[160px] cursor-pointer rounded border-l-8 bg-gray-00 p-1 hover:bg-gray-15  ${
        borderColors[citation.color]
      }`}
      onClick={() =>
        handleCitationClick(citation.documentId, citation.pageNumber)
      }
    >
      <div className="flex items-center">
        <div className="mr-1 text-xs font-bold text-black">
          {citation.ticker}{" "}
        </div>
        <div className="text-[10px]">p. {citation.pageNumber}</div>
      </div>
      <p className="line-clamp-2 text-[10px] font-light leading-3">
        {citation.snippet}
      </p>
    </div>
    )
  }

  return (
    <>   
    {source ? <PdfDialog  documentId={citation.documentId} path={`data/${source.metadata?.file_name}`} trigger={<CitationNode />} url={getStaticFileDataUrl(source.metadata?.file_name as string)}/> : ""}
    </>
  );
};
export default CitationDisplay;