'use client'

import { useState } from "react";
import { ShevronDown, ShevronUp } from "./icons/main-icons";
import { useThreadsStore } from "@/app/store/ThreadsState";
import { MessageCircle } from "lucide-react";

export default function Workspaces() {

    const [isShevronOpen, setShevronIsOpen] = useState<boolean>(true);
    const { threads, selectThread, selectedThread } = useThreadsStore();

    return (    
        <div className="mb-6">
            <div className="flex justify-between items-center text-gray-700 mb-2">
                <div className="font-semibold">Workspaces</div>  
                <button className="bg-transparent border-none" onClick={() => setShevronIsOpen(!isShevronOpen)}>
                    {isShevronOpen ? <ShevronDown /> : <ShevronUp />}
                </button>
            </div>
            {isShevronOpen && threads.map((thread) => (
                <div 
                    key={thread.id} 
                    className={`p-2 mb-2 bg-gray-100 rounded-md shadow-sm hover:bg-gray-200 transition-colors duration-200 flex items-center cursor-pointer ${selectedThread?.id === thread.id ? 'bg-blue-100' : ''}`}
                    onClick={() => selectThread(thread.id)}
                >
                    <MessageCircle className="text-gray-500 mr-2" />
                    <span className="text-gray-800 font-medium mr-2">{thread.title}</span>
                </div>
            ))}
        </div>
    );
}