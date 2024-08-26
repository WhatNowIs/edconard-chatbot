"use client";

import { Button } from "@/app/components/ui/button";
import RecentThreads from "@/app/components/ui/chat/recent-thread";
import Workspaces from "@/app/components/ui/chat/workspace";
import Image from "next/image";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { useState } from "react";
import { PlusIcon } from "./ui/chat/icons/main-icons";

import { useContext } from "react";
import AuthContext from "../context/auth-context";
import ChatContext from "../context/chat-context";
import { ResponseThread } from "../service/thread-service";
import { UserFormType } from "../service/user-service";
import OtherSettings from "./ui/account/other-settings";

export default function LeftNav({
  userThreads,
  userData,
  mode,
}: {
  userThreads: ResponseThread[];
  userData: UserFormType | null;
  mode: boolean;
}) {
  const currentPath = usePathname();
  const chatContext = useContext(ChatContext);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [isButtonDisabled, setIsButtonDisabled] = useState<boolean>(false);

  const authContext = useContext(AuthContext);

  if (!authContext) {
    throw new Error("useContext must be used within an AuthProvider");
  }
  const { user, setUser, setIsResearchExploration } = authContext;

  if (chatContext) {
    const { setThreads, threads } = chatContext;
    threads.length === 0 && setThreads(userThreads);
  }

  if (!user) {
    setUser(userData);
    setIsResearchExploration(mode);
  }

  const handleNewThread = () => {
    setIsLoading(true);
    setIsButtonDisabled(true);
    if (chatContext) {
      chatContext.addThread({
        title: "New thread",
        workspace_id: chatContext.currentWorkspace?.id as string,
        user_id: user?.id as string,
      });
      setIsLoading(false);
      setIsButtonDisabled(false);
    }
  };

  // if (localStorage) console.log(decodeToken(getAccessToken()));

  return (
    <div className="w-80 flex flex-col h-screen overflow-y-auto bg-white border-r border-gray-200 p-4">
      <div className="w-full flex mb-4 justify-between items-center gap-2">
        <Link href={"/"} className="flex gap-2">
          {/* <EdConardLogo /> */}
          <span className="text-2xl">CRI</span>
        </Link>
        {/* <div className="p-2 rounded-md hover:bg-gray-100">
          <Harmburger />
        </div> */}
      </div>
      {user && (
        <div className="flex items-center mb-6 border p-2 rounded-md">
          <Image
            src="https://via.placeholder.com/40"
            alt="Profile Picture"
            width={40}
            height={40}
            className="w-10 h-10 rounded-full mr-3"
          />
          <div>
            <div className="text-sm text-gray-800">{`${user.first_name} ${user.last_name}`}</div>
            <div className="text-gray-500 text-xs">{user.email}</div>
          </div>
        </div>
      )}
      {currentPath !== "/accounts" ? (
        <>
          {user && (
            <>
              <Button
                type="submit"
                className="w-full flex items-center mb-6"
                onClick={handleNewThread}
                disabled={isButtonDisabled}
              >
                {isLoading ? (
                  "Loading..."
                ) : (
                  <>
                    <PlusIcon /> New Thread
                  </>
                )}
              </Button>
              <Workspaces />
              <RecentThreads />
            </>
          )}
        </>
      ) : (
        <>
          <OtherSettings />
        </>
      )}
    </div>
  );
}
