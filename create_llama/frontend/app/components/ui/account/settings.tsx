"use client"

import Link from "next/link";
import { useRouter } from 'next/navigation';



export function Settings(){
    const router = useRouter();

    const onSubmit = () => {
        router.push("/signin");
    }

    return (
        <div className="absolute top-[71%] right-2 z-10 mb-2 w-56 rounded-md bg-white shadow-lg ring-1 ring-black ring-opacity-5 focus:outline-none" role="menu" aria-orientation="vertical" aria-labelledby="menu-button" tabIndex={-1}>
            <div className="py-1" role="none">
                <Link href="/accounts" className="block px-4 py-2 text-sm text-gray-700" role="menuitem" tabIndex={-1} id="menu-item-0">Account settings</Link>
                <Link href="/support" className="block px-4 py-2 text-sm text-gray-700" role="menuitem" tabIndex={-1} id="menu-item-1">Support</Link>
                <Link href="/license" className="block px-4 py-2 text-sm text-gray-700" role="menuitem" tabIndex={-1} id="menu-item-2">License</Link>                
                <button onClick={onSubmit} type="submit" className="block w-full px-4 py-2 text-left text-sm text-gray-700" role="menuitem" tabIndex={-1} id="menu-item-3">Sign out</button>  
            </div>
        </div>
    )
}