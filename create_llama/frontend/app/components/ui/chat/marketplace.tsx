
'use client'

import { useState } from "react";
import { ShevronDown, ShevronUp } from "./icons/main-icons";

export default function Marketplace(
) {

    const [isShevronOpen, setShevronIsOpen] = useState<boolean>(true);

    return (        
        <div>
            <div className="flex justify-between items-center text-gray-700 mb-2">
            <div className="font-semibold">Marketplace</div>
            <button className="bg-transparent border-none" onClick={() => setShevronIsOpen(!isShevronOpen)}>
                {isShevronOpen ? <ShevronDown /> : <ShevronUp />}
            </button>
            </div>
            {isShevronOpen && <div className="text-gray-600">Naval Ravikant</div>}
        </div>
    );
}
