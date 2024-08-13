"use client";
/* eslint-disable @typescript-eslint/no-explicit-any */

import AuthContext from "@/app/context/auth-context";
import ChatContext from "@/app/context/chat-context";
import { getMacroRoundupData } from "@/app/service/user-service";
import { Article } from "@/app/utils/multi-mode-select";
import { useContext, useEffect, useRef, useState } from "react";
import { cn } from "../lib/utils";
import { Switch, SwitchLabel, SwitchThumb } from "../switch";
import { useToast } from "../use-toast";
import ArticleDialog from "./widgets/article-dialog";

export const ChatMode = () => {
  const buttonRef = useRef<HTMLButtonElement>(null);
  const [shouldDrawerOpen, setShouldDrawerOpen] = useState<boolean>(false);
  const authContext = useContext(AuthContext);
  const chatContext = useContext(ChatContext);
  const { toast } = useToast();

  if (!authContext || !chatContext) {
    return <></>;
  }

  const { isResearchExploration, updateChatModeByUser } = authContext;

  const changeChatMode = async (checked: boolean) => {
    const { status, message } = await updateChatModeByUser(checked);

    if (status === 200) {
      toast({
        className: cn(
          "top-0 right-0 flex fixed md:max-w-[420px] md:top-4 md:right-4 text-red-500",
        ),
        title: message,
      });
      setShouldDrawerOpen(checked);
      const article = await getMacroRoundupData();
      chatContext?.setArticle(article as Article);
    } else {
      toast({
        className: cn(
          "top-0 right-0 flex fixed md:max-w-[420px] md:top-4 md:right-4 text-red-500",
        ),
        title: message,
      });
    }
  };

  useEffect(() => {
    if (!shouldDrawerOpen && buttonRef.current && !isResearchExploration) {
      buttonRef.current.click();
      const fetchArticle = async () => {
        const article = await getMacroRoundupData();
        chatContext?.setArticle(article as Article);
      };
      if (!chatContext.article) {
        fetchArticle().catch((error) => console.log(error));
      }
    }
  }, [shouldDrawerOpen]);

  return (
    <div className="w-full h-8 flex bg-white gap-2 items-center justify-start fixed top-0">
      <form>
        <div style={{ display: "flex", alignItems: "center" }}>
          <SwitchLabel
            className="pr-4 text-xs text-gray-600"
            htmlFor="airplane-mode"
          >
            Research/Exploration
          </SwitchLabel>

          <ArticleDialog
            trigger={
              <button type="button" className="hidden" ref={buttonRef}>
                Hidden
              </button>
            }
          />
          {isResearchExploration !== null ? (
            <Switch
              className="SwitchRoot"
              id="airplane-mode"
              onCheckedChange={changeChatMode}
              checked={isResearchExploration}
            >
              <SwitchThumb className="SwitchThumb" />
            </Switch>
          ) : (
            <Switch
              className="SwitchRoot"
              id="airplane-mode"
              onCheckedChange={changeChatMode}
            >
              <SwitchThumb className="SwitchThumb" />
            </Switch>
          )}
        </div>
      </form>
    </div>
  );
};
