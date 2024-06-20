"use client"

import Image from "next/image";
import { usePathname } from 'next/navigation';
import { Button } from "@/app/components/ui/button";
import { EdConardLogo, Harmburger, PlusIcon } from "./ui/chat/icons/main-icons";
import RecentThreads from "@/app/components/ui/chat/recent-thread";
import Workspaces from "@/app/components/ui/chat/workspace";
import ChatBundles from "@/app/components/ui/chat/chat-bundles";
import Marketplace from "@/app/components/ui/chat/marketplace";
import Link from "next/link";
import { useThreadsStore } from "@/app/data/ThreadsState";
import { useState } from "react";

export default function LeftNav() {
    const currentPath = usePathname();
    const { createThread } = useThreadsStore();
    const [isLoading, setIsLoading] = useState<boolean>(false);
    const [isButtonDisabled, setIsButtonDisabled] = useState<boolean>(false);

    const handleNewThread = async (): Promise<void> => {
        setIsLoading(true);
        setIsButtonDisabled(true);
        await createThread("New Thread", "This is a new thread");
        setIsLoading(false);
        setTimeout(() => setIsButtonDisabled(false), 2000);
    };

    return (
        <div className="w-80 flex flex-col h-screen bg-white border-r border-gray-200 p-4">
            <div className="w-full flex mb-4 justify-between items-center gap-2">
                <Link href={"/"} className="flex gap-2">
                    <EdConardLogo />
                    <span className="text-2xl">CRI</span>
                </Link>
                <Harmburger />
            </div>
            <div className="flex items-center mb-6 border p-2 rounded-md">
                <Image 
                    src="https://via.placeholder.com/40" 
                    alt="Profile Picture" 
                    width={40}
                    height={40} 
                    className="w-10 h-10 rounded-full mr-3" 
                />
                <div>
                <div className="text-sm text-gray-500">Marc Hill</div>
                <div className="text-sm text-gray-500 text-xs">mhill@edconard.com</div>
                </div>
            </div>            
            {
                currentPath !== "/accounts" && (
                    <>
                        <Button 
                            type="submit" 
                            className="w-full flex items-center mb-6" 
                            onClick={handleNewThread} 
                            disabled={isButtonDisabled}
                        >
                            {isLoading ? "Loading..." : <><PlusIcon /> New Thread</>}
                        </Button>
                        <Workspaces />
                        
                    </>
                )
            }
        </div>
    );
}
