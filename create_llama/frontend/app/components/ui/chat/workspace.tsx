'use client'

import { useState } from "react";
import { ShevronDown, ShevronUp } from "./icons/main-icons";
import { MessageCircle } from "lucide-react";

export default function Workspaces() {
    const [isShevronOpen, setShevronIsOpen] = useState<boolean>(true);

    return (    
        <div className="mb-6">
            <div className="flex justify-between items-center text-gray-700 mb-2">
                <div className="font-semibold">Workspaces</div>  
                <button className="bg-transparent border-none" onClick={() => setShevronIsOpen(!isShevronOpen)}>
                    {isShevronOpen ? <ShevronDown /> : <ShevronUp />}
                </button>
            </div>
            <div 
                className={`p-2 mb-2 bg-gray-100 rounded-md shadow-sm hover:bg-gray-200 transition-colors duration-200 flex items-center cursor-pointer`}
            >
                <MessageCircle className="text-gray-500 mr-2" />
                <span className="text-gray-800 font-medium mr-2">Edconard workspace</span>
            </div>
        </div>
    );
}