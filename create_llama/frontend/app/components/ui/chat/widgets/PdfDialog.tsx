import { PDFViewer, PdfFocusProvider } from "@llamaindex/pdf-viewer";
import { Button } from "../../button";
import {
  Drawer,
  DrawerClose,
  DrawerContent,
  DrawerDescription,
  DrawerHeader,
  DrawerTitle,
  DrawerTrigger,
} from "../../drawer";
import { useCallback, useEffect, useRef, useState } from "react";
import { OBSERVER_THRESHOLD_PERCENTAGE } from "./pdfDisplayConstants";
import { useInView } from "react-intersection-observer";
import { usePdfFocus } from "@/app/context/pdf";
import debounce from "lodash.debounce";

export interface PdfDialogProps {
  documentId: string;
  path: string;
  url: string;
  trigger: React.ReactNode;
  scale: number;
  pageNumber: number;
  setPageInView: (n: number) => void;
}

export default function PdfDialog(props: PdfDialogProps) {
  const { pdfFocusState } = usePdfFocus();
  const [isHighlighted, setIsHighlighted] = useState(false);
   // Get which page is in view from an intersection observer
   const { ref: inViewRef, inView } = useInView({
    threshold: OBSERVER_THRESHOLD_PERCENTAGE * Math.min(1 / props.scale, 1),
  });

  const containerRef = useRef<HTMLDivElement>(null);

  // Use `useCallback` so we don't recreate the function on each render
  // Need to set two Refs, one for the intersection observer, one for the container
  const setRefs = useCallback(
    (node: HTMLDivElement | null | undefined) => {
      // Ref's from useRef needs to have the node assigned to `current`
      (containerRef as React.MutableRefObject<HTMLDivElement | null>).current =
        node as HTMLDivElement | null;

      // Callback refs, like the one from `useInView`, is a function that takes the node as an argument
      inViewRef(node);
    },
    [inViewRef]
  );

  useEffect(() => {
    if (inView) {
      props.setPageInView(props.pageNumber);
    }
  }, [inView, props.pageNumber, props.setPageInView, inViewRef]);


  const documentFocused = pdfFocusState.documentId === props.documentId;

  useEffect(() => {
    maybeHighlight();
  }, [documentFocused, inView]);

  const maybeHighlight = useCallback(
    debounce(() => {
      if (
        documentFocused &&
        pdfFocusState.citation?.pageNumber === props.pageNumber + 1 &&
        !isHighlighted
      ) {
        multiHighlight(
          pdfFocusState.citation?.snippet,
          props.pageNumber,
          pdfFocusState.citation?.color
        );
        setIsHighlighted(true);
      }
    }, 50),
    [pdfFocusState.citation?.snippet, props.pageNumber, isHighlighted]
  );


  return (
    <Drawer direction="left">
      <DrawerTrigger>{props.trigger}</DrawerTrigger>
      <DrawerContent className="w-3/5 mt-24 h-full max-h-[96%] ">
        <DrawerHeader className="flex justify-between">
          <div className="space-y-2">
            <DrawerTitle>PDF Content</DrawerTitle>
            <DrawerDescription>
              File path:{" "}
              <a
                className="hover:text-blue-900"
                href={props.url}
                target="_blank"
              >
                {props.path}
              </a>
            </DrawerDescription>
          </div>
          <DrawerClose asChild>
            <Button variant="outline">Close</Button>
          </DrawerClose>
        </DrawerHeader>
        <div className="m-4"  ref={setRefs}>
          <PdfFocusProvider>
            <PDFViewer
              file={{
                id: props.documentId,
                url: props.url,
              }}
            />
          </PdfFocusProvider>
        </div>
      </DrawerContent>
    </Drawer>
  );
}
function multiHighlight(snippet: any, pageNumber: any, color: any) {
  throw new Error("Function not implemented.");
}

