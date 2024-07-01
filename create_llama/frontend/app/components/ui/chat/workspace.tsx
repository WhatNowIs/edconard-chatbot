'use client'

import React from 'react'; 
import { useState } from "react";
import { ShevronDown, ShevronUp } from "./icons/main-icons";
// import { MessageCircle } from "lucide-react";

export default function Workspaces() {
    const [isShevronOpen, setShevronIsOpen] = useState<boolean>(true);

    return (    
        <div className="mb-4">
            <div className="flex justify-between items-center text-gray-700 mb-2">
                <div className="font-semibold text-sm">Workspaces</div>  
                <button className="bg-transparent border-none" onClick={() => setShevronIsOpen(!isShevronOpen)}>
                    {isShevronOpen ? <ShevronDown /> : <ShevronUp />}
                </button>
            </div>
           {isShevronOpen && (
                <div className={`flex justify-between text-gray-600 text-xs my-1 cursor-pointer hover:bg-gray-100 hover:rounded-md p-2`}>
                    {/* <MessageCircle className="text-gray-500 mr-2" /> */}
                    <span className="mr-2">Edconard workspace</span>
                </div>
            )}
        </div>
    );
}