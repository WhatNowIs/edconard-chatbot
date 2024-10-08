"use client";

import AuthContext from "@/app/context/auth-context";
import ChatContext from "@/app/context/chat-context";
import { useContext, useEffect, useState } from "react";
import { ShevronDown, ShevronUp } from "./icons/main-icons";

export default function RecentThreads() {
  const [isShevronOpen, setShevronIsOpen] = useState<boolean>(true);
  const authContext = useContext(AuthContext);
  const chatContext = useContext(ChatContext);

  if (!authContext || !chatContext) {
    throw new Error(
      "useContext must be used within an AuthProvider and ChatProvider",
    );
  }
  const { user } = authContext;
  const { threads, loadThreads, selectThread, selectedThread } = chatContext;

  useEffect(() => {
    if (user && threads.length === 0) {
      loadThreads();
    }
  }, []);

  const onSelect = (threadId: string) => {
    selectThread(threadId);
  };

  return (
    <div className="mb-2">
      <div className="flex justify-between items-center text-gray-800 mb-2">
        <div className="font-sans text-sm">Recent Threads</div>
        <button
          className="bg-transparent border-none"
          onClick={() => setShevronIsOpen(!isShevronOpen)}
        >
          {isShevronOpen ? <ShevronDown /> : <ShevronUp />}
        </button>
      </div>
      {isShevronOpen &&
        threads &&
        threads
          .slice()
          .reverse()
          .map((thread) => (
            <div
              key={thread.id}
              onClick={() => onSelect(thread.id)}
              className={`flex justify-between text-gray-600 text-xs my-1 cursor-pointer hover:bg-gray-100 hover:rounded-md p-2 ${selectedThread?.id === thread.id ? "bg-gray-100 rounded-md" : ""}`}
            >
              <span>
                {thread.title.length > 30
                  ? `${thread.title.substring(0, 30)}...`
                  : thread.title.substring(0, 30)}
              </span>
            </div>
          ))}
    </div>
  );
}
