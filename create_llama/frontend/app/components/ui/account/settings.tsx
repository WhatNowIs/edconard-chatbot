"use client"

import AuthContext from "@/app/context/auth-context";
import Link from "next/link";
import { useRouter } from 'next/navigation';
import { useContext } from "react";

export function Settings(){
    const router = useRouter();
    const authContext = useContext(AuthContext);
    
    if (!authContext) {
        throw new Error('useContext must be used within an AuthProvider');
    }

    const { logout } = authContext;

    const signout = () => {
        logout();
        router.push("/signin");
    }


    return (
        <div className="absolute top-[71%] right-2 z-10 mb-2 w-56 rounded-md bg-white shadow-lg ring-1 ring-black ring-opacity-5 focus:outline-none" role="menu" aria-orientation="vertical" aria-labelledby="menu-button" tabIndex={-1}>
            <div className="py-1 px-3" role="none">
                <Link href="/accounts" className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 rounded-md" role="menuitem" tabIndex={-1} id="menu-item-0">Account settings</Link>
                <Link href="/support" className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 rounded-md" role="menuitem" tabIndex={-1} id="menu-item-1">Help & FAQ</Link>
                <Link href="/license" className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 rounded-md" role="menuitem" tabIndex={-1} id="menu-item-2">License</Link>         
                <Link href="/license" className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 rounded-md" role="menuitem" tabIndex={-1} id="menu-item-2">Terms and Policies</Link>               
                <button onClick={signout} type="submit" className="block w-full px-4 py-2 text-left text-sm text-gray-700 hover:bg-gray-100 rounded-md" role="menuitem" tabIndex={-1} id="menu-item-3">Sign out</button>  
            </div>
        </div>
    )
}