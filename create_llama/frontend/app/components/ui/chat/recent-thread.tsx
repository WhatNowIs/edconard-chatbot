
'use client'

import { useContext, useEffect, useState } from "react";
import { ShevronDown, ShevronUp } from "./icons/main-icons";
import ChatContext from "@/app/context/chat-context";
import AuthContext from "@/app/context/auth-context";
import { HiMiniPencil } from "react-icons/hi2";

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
        if (user) {
            loadThreads();
        }
    }, []);

    // useEffect(() => {
    //     if(selectedThread){

    //     }

    // }, [selectedThread]);

    const onSelect = (threadId: string) => {
        selectThread(threadId)
    }

    return (    
        <div className="mb-6">
            <div className="flex justify-between items-center text-gray-700 mb-2">
            <div className="font-semibold">Recent Threads</div>
                <button className="bg-transparent border-none" onClick={() => setShevronIsOpen(!isShevronOpen)}>
                    {isShevronOpen ? <ShevronDown /> : <ShevronUp />}
                </button>
            </div>
            {
                isShevronOpen && threads && threads.slice().reverse().map((thread) => (
                    <div 
                        onClick={() => onSelect(thread.id)}
                        className={`flex justify-between text-gray-600 my-2 cursor-pointer p-2 ${selectedThread?.id === thread.id ? "bg-gray-100 rounded-md": ""}`}>
                        <span>{thread.title}</span>
                        {/* <HiMiniPencil/> */}
                    </div>
                ))
            }
        </div>
    );
}
