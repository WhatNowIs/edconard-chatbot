import React from 'react'; 
import { ChevronDown, ChevronRight, Loader2 } from "lucide-react";
import { useState } from "react";
import { Button } from "../button";
import {
  Collapsible,
  CollapsibleContent,
  CollapsibleTrigger,
} from "../collapsible";
import { EventData, SourceNode } from "./index";
import CitationDisplay from "./widgets/citation-display";
import { DocumentColorEnum } from "@/app/utils/colors";

export function ChatEvents({
  data,
  citations,
  isLoading,
}: {
  data: EventData[];
  citations: SourceNode[];
  isLoading: boolean;
}) {
  const [isOpen, setIsOpen] = useState(false);

  const buttonLabel = isOpen ? "Hide events" : "Show events";

  const EventIcon = isOpen ? (
    <ChevronDown className="h-4 w-4" />
  ) : (
    <ChevronRight className="h-4 w-4" />
  );

  return (
    <div className="border-l-2 border-gray-800 pl-2">
      <Collapsible open={isOpen} onOpenChange={setIsOpen}>
        <CollapsibleTrigger asChild>
          <Button variant="secondary" className="space-x-2">
            {isLoading ? <Loader2 className="h-4 w-4 animate-spin" /> : null}
            <span>{buttonLabel}</span>
            {EventIcon}
          </Button>
        </CollapsibleTrigger>
        <CollapsibleContent asChild>
        <div>
          <div className="mt-4 text-sm space-y-2">
            {data.map((eventItem: EventData, index: number) => (
              <div key={index}>{eventItem.title}</div>
            ))}
          </div>
          {
            citations.map((citation) => (
            <CitationDisplay 
              key={citation.id}
              citation={{ 
                documentId: citation.id,
                snippet: citation.text,
                pageNumber: citation.metadata?.page_label as number,
                ticker: citation.metadata?.file_name as string,
                color: DocumentColorEnum.gray,
              }}
              source={citation} 
            />))
          }
          </div>          
        </CollapsibleContent>
      </Collapsible>
    </div>
  );
}
