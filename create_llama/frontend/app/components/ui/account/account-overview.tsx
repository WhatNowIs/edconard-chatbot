
"use client"

import React from 'react'; 
import { useContext } from "react";
import AuthContext from "@/app/context/auth-context";
import { Input } from "../input";
import { Button } from "../button";
import { UserFormType } from "@/app/service/user-service";

export default function AccountOverview({ userData }: { userData: UserFormType; }){
    const authContext = useContext(AuthContext);
    
    if (!authContext) {
        throw new Error('useContext must be used within an AuthProvider');
    }
    const { user, setUser } = authContext;

    if(!user){
        setUser(userData);
    }

    return (        
        <form className="md:col-span-2">
            <h1 className="md:col-span-1 text-gray-800 text-3xl">Account Settings</h1>
        <div className="grid grid-cols-1 gap-x-6 gap-y-8 sm:max-w-xl sm:grid-cols-6 my-6">
            <div className="sm:col-span-3">
                <label htmlFor="first-name" className="block text-sm font-medium leading-6 ">
                    First name
                </label>
                <div className="mt-2">
                    <Input
                        autoFocus
                        name="message"
                        placeholder="First name"
                        className="flex-1"
                        value={user?.first_name}
                    />
                </div>
            </div>

            <div className="sm:col-span-3">
                <label htmlFor="last-name" className="block text-sm font-medium leading-6 ">
                    Last name
                </label>
                <div className="mt-2">                            
                    <Input
                        autoFocus
                        name="message"
                        placeholder="Last name"
                        className="flex-1"
                        value={user?.last_name}
                    />
                </div>
            </div>

            <div className="col-span-full">
                <label htmlFor="email" className="block text-sm font-medium leading-6">
                    Email address
                </label>
                <div className="mt-2">                     
                    <Input
                        type="email"
                        autoFocus
                        name="message"
                        placeholder="Email address"
                        className="flex-1"
                        value={user?.email}
                    />
                </div>
            </div>

            <div className="col-span-full">
                <label htmlFor="timezone" className="block text-sm font-medium leading-6">
                    Timezone
                </label>
                <div className="mt-2">
                    <select
                    id="timezone"
                    name="timezone"
                    className="block w-full rounded-md border-0 bg-white/5 py-1.5  shadow-sm ring-1 ring-inset ring-white/10 focus:ring-2 focus:ring-inset focus:ring-indigo-500 sm:text-sm sm:leading-6 [&_*]:text-black"
                    >
                        <option>Pacific Standard Time</option>
                        <option>Eastern Standard Time</option>
                        <option>Greenwich Mean Time</option>
                    </select>
                </div>
            </div>
        </div>

        <div className="mt-8 flex">
            <Button>
                Save
            </Button>
        </div>
    </form>
    )
}