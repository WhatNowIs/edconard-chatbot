
'use client'

import { useState } from "react";
import { ShevronDown, ShevronUp } from "./icons/main-icons";

export default function RecentThreads(
) {

    const [isShevronOpen, setShevronIsOpen] = useState<boolean>(true);

    return (    
        <div className="mb-6">
            <div className="flex justify-between items-center text-gray-700 mb-2">
            <div className="font-semibold">Recent Threads</div>
                <button className="bg-transparent border-none" onClick={() => setShevronIsOpen(!isShevronOpen)}>
                    {isShevronOpen ? <ShevronDown /> : <ShevronUp />}
                </button>
            </div>
            {
                isShevronOpen && (
                    <>
                        <div className="text-gray-600 my-2 cursor-pointer">Capitalisms Class Debate</div>
                        <div className="text-gray-600 my-2 cursor-pointer">Capitalisms Impact</div>
                        <div className="text-gray-600 my-2 cursor-pointer">Capitalisms Effectiveness</div>
                        <div className="text-gray-600 my-2 cursor-pointer">Untitled Thread</div>
                    </>
                )
            }
        </div>
    );
}
