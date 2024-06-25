
'use client'

import React from 'react'; 
import { useState } from "react";
import { ShevronDown, ShevronUp } from "./icons/main-icons";

export default function ChatBundles(
) {

    const [isShevronOpen, setShevronIsOpen] = useState<boolean>(true);

    return (        
        <div className="mb-6">
            <div className="flex justify-between items-center text-gray-700 mb-2">
            <div className="font-semibold">Chat Bundles</div> 
                <button className="bg-transparent border-none" onClick={() => setShevronIsOpen(!isShevronOpen)}>
                    {isShevronOpen ? <ShevronDown /> : <ShevronUp />}
                </button>
            </div>
        </div>
    );
}
