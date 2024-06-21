"use client"

import { useEffect, useRef, useState } from 'react';
import { HiMiniCog6Tooth  } from 'react-icons/hi2';
import { Settings } from './ui/account/settings';
export default function RightNav(){
    const [isSettingOpen, setIsSettingsOpen] = useState<boolean>(false);

    const settingsRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        function handleClickOutside(event: MouseEvent) {
            if (settingsRef.current && !settingsRef.current.contains(event.target as Node)) {
                setIsSettingsOpen(false);
            }
        }

        document.addEventListener('mousedown', handleClickOutside);
        return () => {
            document.removeEventListener('mousedown', handleClickOutside);
        };
    }, [settingsRef]);

    return (
        <div className="flex flex-col justify-between items-center w-14 h-screen bg-white border-l border-gray-200 p-4">
            <div className="mb-6">
                <button className="w-full h-5 flex items-center px-4 py-2 bg-gray-100 text-gray-700 rounded-lg mb-4">
                </button>
                <button className="w-full h-5 flex items-center px-4 py-2 bg-gray-100 text-gray-700 rounded-lg mb-4">
                </button>
                <button className="w-full h-5 flex items-center px-4 py-2 bg-gray-100 text-gray-700 rounded-lg">
                </button>
            </div>
            <div ref={settingsRef}>
                {isSettingOpen && <Settings />}
                <button className="flex items-center" onClick={() => setIsSettingsOpen(!isSettingOpen)}>                    
                    <HiMiniCog6Tooth className='w-6 h-6' />
                </button>
            </div>

      </div>
    )
}