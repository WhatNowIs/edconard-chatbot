
'use client'

import React from 'react'; 
import { useContext, useEffect, useState } from "react";
import { ShevronDown, ShevronUp } from "./icons/main-icons";
import ChatContext from "@/app/context/chat-context";
import AuthContext from "@/app/context/auth-context";

export default function RecentThreads() {    
    const [isShevronOpen, setShevronIsOpen] = useState<boolean>(true);
    const authContext = useContext(AuthContext);
    const chatContext = useContext(ChatContext);

    if (!authContext || !chatContext) {
        throw new Error('useContext must be used within an AuthProvider and ChatProvider');
    }
    const { user } = authContext;
    const { threads, loadThreads, selectThread, selectedThread } = chatContext;

    useEffect(() => {
        if (user && threads.length === 0) {
            loadThreads();
        }
    }, []);

    const onSelect = (threadId: string) => {
        selectThread(threadId)
    }

    console.log("threads-------:", threads);

    return (    
        <div className="mb-6">
            <div className="flex justify-between items-center text-gray-700 mb-2">
            <div className="font-semibold">Recent Threads</div>
                <button className="bg-transparent border-none" onClick={() => setShevronIsOpen(!isShevronOpen)}>
                    {isShevronOpen ? <ShevronDown /> : <ShevronUp />}
                </button>
            </div>
            {
                (isShevronOpen && threads) && threads.slice().reverse().map((thread) => (
                    <div 
                        key={thread.id}
                        onClick={() => onSelect(thread.id)}
                        className={`flex justify-between text-gray-600 text-sm my-2 cursor-pointer p-2 ${selectedThread?.id === thread.id ? "bg-gray-100 rounded-md": ""}`}>
                        <span>{thread.title}</span>
                        {/* <HiMiniPencil/> */}
                    </div>
                ))
            }
        </div>
    );
}
