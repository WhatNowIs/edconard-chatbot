import Image from "next/image";
import { Button } from "./ui/button";
import { EdConardLogo, Harmburger, PlusIcon, ShevronDown } from "./ui/chat/icons/main-icons";
import RecentThreads from "./ui/chat/recent-thread";
import Workspaces from "./ui/chat/workspace";
import ChatBundles from "./ui/chat/chat-bundles";
import Marketplace from "./ui/chat/marketplace";



export default function LeftNav() {



    return (
        <div className="w-64 flex flex-col h-screen bg-white border-r border-gray-200 p-4">
            <div className="w-full flex mb-4 justify-between items-center gap-2">
                <div className="flex gap-2">
                    <EdConardLogo />
                    <span className="text-2xl">CRI</span>
                </div>
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
            
            <Button type="submit" className="w-full flex items-center mb-6">
                <PlusIcon />
                New Thread
            </Button>
            <Workspaces />
            <RecentThreads />
            <ChatBundles />
            <Marketplace />
        </div>
    );
}
