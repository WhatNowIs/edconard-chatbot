import { PdfFocusProvider } from "@/app/context/pdf";
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
import { ViewPdf } from "../pdf-viewer/ViewPdf";

export interface PdfDialogProps {
  documentId: string;
  path: string;
  url: string;
  trigger: React.ReactNode;
}

export default function PdfDialog(props: PdfDialogProps) {

  return (
    <Drawer direction="left">
      <DrawerTrigger>{props.trigger}</DrawerTrigger>
      <DrawerContent className="w-3/5 mt-24 h-full max-h-[96%] ">
        <DrawerHeader className="flex justify-between">
          <div className="space-y-2">
            <DrawerTitle>PDF Content Modified</DrawerTitle>
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
        <div className="m-4">
          <PdfFocusProvider>
            <ViewPdf
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

