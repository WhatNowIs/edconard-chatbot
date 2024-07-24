import {
  Drawer,
  DrawerClose,
  DrawerContent,
  DrawerHeader,
  DrawerTitle,
  DrawerTrigger,
} from "@/app/components/ui/drawer";
import React, { useRef } from "react";
import { Button } from "../../button";
import MacroRoundupForm from "./article-dialog-form";

export interface ArticleDialogProps {
  trigger: React.ReactNode;
}

export default function ArticleDialog(props: ArticleDialogProps) {
  const buttonRef = useRef<HTMLButtonElement>(null);
  const close = () => {
    if (buttonRef && buttonRef.current) {
      buttonRef.current.click();
    }
  };

  return (
    <Drawer direction="left">
      <DrawerTrigger>{props.trigger}</DrawerTrigger>
      <DrawerContent className="w-96 mt-8 h-full max-h-[98%]">
        <DrawerHeader className="flex justify-between">
          <div className="space-y-2">
            <DrawerTitle>Macro-roundup article info</DrawerTitle>
          </div>
          <DrawerClose asChild>
            <Button ref={buttonRef} variant="outline">
              Close
            </Button>
          </DrawerClose>
        </DrawerHeader>
        <div className="px-4">
          <MacroRoundupForm close={close} />
        </div>
      </DrawerContent>
    </Drawer>
  );
}
