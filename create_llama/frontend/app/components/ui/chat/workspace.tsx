
'use client'

import { useState } from "react";
import { ShevronDown, ShevronUp } from "./icons/main-icons";

export default function Workspaces(
) {

    const [isShevronOpen, setShevronIsOpen] = useState<boolean>(true);

    return (    
        <div className="mb-6">
            <div className="flex justify-between items-center text-gray-700 mb-2">
            <div className="font-semibold">Workspaces</div>  
            <button className="bg-transparent border-none" onClick={() => setShevronIsOpen(!isShevronOpen)}>
                {isShevronOpen ? <ShevronDown /> : <ShevronUp />}
            </button>
            </div>
            {isShevronOpen && <div className="text-gray-600">Edward Conard's Co...</div>}
        </div>
    );
}
