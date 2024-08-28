"use client";

import AuthContext from "@/app/context/auth-context";
import ChatContext from "@/app/context/chat-context";
import { useContext, useState } from "react";
import { ShevronDown, ShevronUp } from "./icons/main-icons";

export default function Workspaces() {
  const [isShevronOpen, setShevronIsOpen] = useState<boolean>(true);
  const chatContext = useContext(ChatContext);
  const authContext = useContext(AuthContext);

  if (!chatContext || !authContext) return <></>;

  const { currentWorkspace, setCurrentWorkspace, workspaces, loadThreads } =
    chatContext;

  const onSelect = (workspace_Id: string) => {
    const currentWS = workspaces.find(
      (workspace) => workspace.id === workspace_Id,
    );
    currentWS && setCurrentWorkspace(currentWS);
    loadThreads(currentWS?.id as string);
  };

  return (
    <div className="mb-4">
      <div className="flex justify-between items-center text-gray-800 mb-2">
        <div className="font-sans text-sm">Workspaces</div>
        <button
          className="bg-transparent border-none"
          onClick={() => setShevronIsOpen(!isShevronOpen)}
        >
          {isShevronOpen ? <ShevronDown /> : <ShevronUp />}
        </button>
      </div>

      {isShevronOpen &&
        workspaces &&
        workspaces
          .slice()
          .reverse()
          .map((workspace) => (
            <div
              key={workspace.id}
              onClick={() => onSelect(workspace.id)}
              className={`flex justify-between text-gray-600 text-xs my-1 cursor-pointer hover:bg-gray-100 hover:rounded-md p-2 ${currentWorkspace?.id === workspace.id ? "bg-gray-100 rounded-md" : ""}`}
            >
              <span>
                {workspace.name.length > 30
                  ? `${workspace.name.substring(0, 30)}...`
                  : workspace.name.substring(0, 30)}
              </span>
            </div>
          ))}
    </div>
  );
}
