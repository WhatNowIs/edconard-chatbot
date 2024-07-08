"use client"
/* eslint-disable @typescript-eslint/no-explicit-any */

import React, { useContext } from "react";
import AuthContext from "@/app/context/auth-context";
import { useToast } from "../use-toast";
import { cn } from "../lib/utils";
import { Switch, SwitchLabel, SwitchThumb } from "../switch";

export const ChatMode = () => {
    const authContext = useContext(AuthContext);
    const { toast } = useToast()

    if(!authContext){
      return <></>
    }

    const { isResearchExploration, updateChatModeByUser } = authContext;
    console.log(isResearchExploration);

  
    const changeChatMode = async (checked: boolean) => {
      const {  status, message } = await updateChatModeByUser(checked);

      if(status === 200){      
        toast({
          className: cn(
          "top-0 right-0 flex fixed md:max-w-[420px] md:top-4 md:right-4 text-red-500",
          ),
          title: message,
        }); 
      }
      else{        
        toast({
          className: cn(
          "top-0 right-0 flex fixed md:max-w-[420px] md:top-4 md:right-4 text-red-500",
          ),
          title: message,
        });    
      }
    };
  
    return (
        <div className="w-[40%] h-8 flex gap-2 items-center justify-start">          
          <form>
            <div style={{ display: 'flex', alignItems: 'center' }}>
              <SwitchLabel className="pr-4" htmlFor="airplane-mode">
                Research/Exploration
              </SwitchLabel>
              <Switch className="SwitchRoot" id="airplane-mode" onCheckedChange={changeChatMode}>
                <SwitchThumb className="SwitchThumb" />
              </Switch>
            </div>
          </form>
        </div>
    );
  };
  