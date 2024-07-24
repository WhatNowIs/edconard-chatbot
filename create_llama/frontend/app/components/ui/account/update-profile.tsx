"use client"

import React, { useEffect } from 'react'; 
import { useRef, ChangeEvent, useState } from "react";
import { Input } from "../input";
import Image from "next/image";
import { UserFormType } from "@/app/service/user-service";

export default function UpdateProfile({ user }: { user: UserFormType; }){
    const [fileUrl, setFileUrl] = useState<string>("https://via.placeholder.com/80");
    const [fileName, setFileName] = useState<string>("Change profile");
    const fileInputRef = useRef<HTMLInputElement>(null);
  
    const handleButtonClick = () => {
      if (fileInputRef.current) {
        fileInputRef.current.click();
      }
    };

    const truncateString = (str: string, num: number) => {
        if (str.length <= num) {
            return str;
        }
        return str.slice(0, num) + '...';
    };
      
  
    const handleFileChange = (event:  ChangeEvent<HTMLInputElement>) => {
      const files = event.target.files as FileList;
      if (files.length > 0) {
        const file = files[0];
        if (file) {
          const reader = new FileReader();
          setFileName(truncateString(file.name, 14));
          reader.onloadend = () => {
            setFileUrl(reader.result as string);
          };
          reader.readAsDataURL(file);
        }
      }
    };

    useEffect(() => {
      console.log(user);
    }, [user]);

    return (
        <div>                        
            <div className="col-span-full flex items-center gap-x-8">
                <div className="rounded-lg p-1 border-2 border-gray-200">
                    <Image
                        onClick={handleButtonClick}
                        src={fileUrl}
                        alt="Profile picture"
                        width={96}
                        height={96}
                        className="h-24 w-24 flex-none rounded-lg bg-gray-800 object-cover cursor-pointer"
                    />
                </div>
                <Input 
                    type="file"
                    ref={fileInputRef}
                    onChange={handleFileChange}
                    className="hidden"
                />
                <div>
                    <button
                        onClick={handleButtonClick}
                        type="button"
                        className="rounded-md bg-white/10 px-3 py-2 text-sm font-semibold  shadow-sm hover:bg-white/20"
                        >
                        {fileName}
                    </button>
                    <p className="mt-2 text-xs leading-5 text-gray-400">JPG, GIF or PNG. 1MB max.</p>
                </div>
            </div>
        </div>
    )
}