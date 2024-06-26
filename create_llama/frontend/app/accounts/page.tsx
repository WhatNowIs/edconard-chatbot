import React from 'react'; 
import LeftNav from "@/app/components/left-nav";
import RightNav from "@/app/components/right-nav";
import { Button } from "@/app/components/ui/button";
import { Input } from "@/app/components/ui/input";
import UpdateProfile from "@/app/components/ui/account/update-profile";
import AccountOverview from "@/app/components/ui/account/account-overview"
import { cookies } from 'next/headers';
import { redirect } from 'next/navigation';
import { ResponseThread } from "@/app/service/thread-service";
import { Suspense } from "react";
import { UserFormType, getChatMode } from '../service/user-service';

async function getThreads(token: string): Promise<ResponseThread[]> {  
    const threadResponse = await fetch(`${process.env.NEXT_PUBLIC_BASE_URL}/api/threads`, {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });
    if (!threadResponse.ok) {
        return []
    }  
    return await threadResponse.json() as ResponseThread[];  
}  
  
async function getUser(token: string): Promise<{ user: UserFormType | null; mode: string | null;}>{  
    const response = await fetch(`${process.env.NEXT_PUBLIC_BASE_URL}/api/auth/me`, {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });
    if (!response.ok) {
        return { user: null, mode: null }
    }  
    const user = await response.json() as UserFormType;  
    const { mode } = await getChatMode(user.id as string, token)  
  
    return { user, mode }   
}
  
export default async function AccountSettings() { 
    const token = cookies().get('access_token');
    
    if (!token) {
        redirect('/signin');
    }

    const threadData = token.value ? await getThreads(token.value as string) : [];
    const userData = token?.value ? await getUser(token.value as string) : {user: null, mode: null};

    return (        
        <Suspense fallback={<div>Loading...</div>}>
            <div className="w-full flex h-screen">
                    <LeftNav userThreads={threadData} userData={userData.user} mode={userData.mode}/>
                    <main className="w-full h-screen items-center flex flex-col overflow-auto">
                        <div className="grid w-full grid-cols-1 gap-y-10 px-4 py-16 sm:px-6 md:grid-cols-3 lg:px-8 py-6">
                            <UpdateProfile user={userData.user as UserFormType} />
                            <AccountOverview userData={userData.user as UserFormType} />
                        </div>

                        <div className="grid w-full grid-cols-1 gap-y-10 px-4 py-16 sm:px-6 md:grid-cols-3 lg:px-8">
                            <div>
                                <h2 className="text-base font-semibold leading-7 ">Change password</h2>
                                <p className="mt-1 text-sm leading-6 text-gray-400">
                                    Update your password associated with your account.
                                </p>
                            </div>

                            <form className="md:col-span-2">
                                <div className="grid grid-cols-1 gap-x-6 gap-y-4 sm:max-w-xl sm:grid-cols-6">
                                    <div className="col-span-full">
                                        <label htmlFor="current-password" className="block text-sm font-medium leading-6 ">
                                            Current password
                                        </label>
                                        <div className="mt-2">                     
                                            <Input
                                                autoFocus
                                                name="message"
                                                placeholder="Current message"
                                                className="flex-1"
                                            />
                                        </div>
                                    </div>

                                    <div className="col-span-full">
                                        <label htmlFor="new-password" className="block text-sm font-medium leading-6 ">
                                            New password
                                        </label>
                                        <div className="mt-2">                     
                                            <Input
                                                autoFocus
                                                name="message"
                                                placeholder="New password"
                                                className="flex-1"
                                            />
                                        </div>
                                    </div>

                                    <div className="col-span-full">
                                        <label htmlFor="confirm-password" className="block text-sm font-medium leading-6 ">
                                            Confirm password
                                        </label>
                                        <div className="mt-2">                     
                                            <Input
                                                autoFocus
                                                name="message"
                                                placeholder="Confirm password"
                                                className="flex-1"
                                            />
                                        </div>
                                    </div>
                                </div>
                                <div className="mt-8 flex">
                                    <Button >
                                        Save
                                    </Button>
                                </div>
                            </form>
                        </div>

                        <div className="grid w-full grid-cols-1 gap-y-10 gap-x-4 px-4 py-16 sm:px-6 md:grid-cols-3 lg:px-8">
                            <div>
                                <h2 className="text-base font-semibold leading-7 ">Log out other sessions</h2>
                                <p className="mt-1 text-sm leading-6 text-gray-400">
                                    Please enter your password to confirm you would like to log out of your other sessions across all of
                                    your devices.
                                </p>
                            </div>

                            <form className="md:col-span-2">
                                <div className="grid grid-cols-1 gap-x-6 gap-y-8 sm:max-w-xl sm:grid-cols-6">
                                    <div className="col-span-full">
                                    <label htmlFor="logout-password" className="block text-sm font-medium leading-6 ">
                                        Your password
                                    </label>
                                    <div className="mt-2">                     
                                        <Input
                                            autoFocus
                                            name="message"
                                            placeholder="Your password"
                                            className="flex-1"
                                        />
                                    </div>
                                    </div>
                                </div>

                                <div className="mt-8 flex">
                                    <Button>
                                        Log out other sessions
                                    </Button>
                                </div>
                            </form>
                        </div>

                        <div className="grid w-full grid-cols-1 gap-y-10 px-4 py-16 sm:px-6 md:grid-cols-3 lg:px-8">
                            <div>
                                <h2 className="text-base font-semibold leading-7 ">Delete account</h2>
                                <p className="mt-1 text-sm leading-6 text-gray-400">
                                    No longer want to use our service? You can delete your account here. This action is not reversible.
                                    All information related to this account will be deleted permanently.
                                </p>
                            </div>

                            <form className="flex items-start md:col-span-2">                    
                                <button
                                    type="submit"
                                    className="rounded-md bg-red-500 px-3 py-2 mt-1 text-sm font-semibold text-white shadow-sm hover:bg-red-400"
                                >
                                    Yes, delete my account
                                </button>
                            </form>
                        </div>
                    </main>
                <RightNav />
            </div>
        </Suspense>
    )
}
