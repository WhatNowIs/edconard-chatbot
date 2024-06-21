import { SourceNode } from "./index";
import CitationDisplay from "./widgets/citation-display";
import { Citation } from "@/app/types/threads";
import { DocumentColorEnum, borderColors } from '@/app/utils/colors'

export function ChatData({
  data,
}: {
  data: SourceNode[];
}) {

  return (
    
    <div className=" mr-2 flex w-full overflow-x-scroll pl-2 ">
    {data?.map(
      (citation, citationIndex) => {
        
        if(citation.metadata){
            return (
              <CitationDisplay
                key={`${citation.id}-${citationIndex}`}
                citation={
                  {
                    documentId: citation.id,
                    snippet: citation.text,
                    pageNumber: citation.metadata?.page_label as number,
                    ticker: citation.metadata?.file_name,
                    color: DocumentColorEnum.gray,
                  } as Citation
                }
                source={citation}
              />
            );
          }
        }
    )}
  </div>
  );
}
