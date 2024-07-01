"use client"
/* eslint-disable @typescript-eslint/no-explicit-any */

import React, { useContext } from "react";
import { supportedChatMode } from "@/app/utils/multi-mode-select";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/app/components/ui/select';
import AuthContext from "@/app/context/auth-context";
import { useToast } from "../use-toast";
import { cn } from "../lib/utils";

export const ChatMode = () => {
    const authContext = useContext(AuthContext);
    const { toast } = useToast()

    if(!authContext){
      return <></>
    }

    const { chatMode, updateChatModeByUser } = authContext;
    console.log(chatMode);

  
    const changeChatMode = async (chatMode: string) => {
      const {  status, message } = await updateChatModeByUser(chatMode);

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
        <div className="w-[35%] h-8 flex gap-2 items-center justify-start">
          <label className="text-md font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70 mr-2">Mode</label>
          <Select
            defaultValue={chatMode as string}
            onValueChange={changeChatMode}

          >
            <SelectTrigger>
              <SelectValue placeholder="Research/Exploration" />
            </SelectTrigger>
            <SelectContent>
              {supportedChatMode.map((chatMode) => (
                <SelectItem className="text-xs" key={chatMode.value} value={chatMode.value}>
                  {chatMode.name}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
    );
  };
  