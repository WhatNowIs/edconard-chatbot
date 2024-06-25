import React from 'react'; 
import ChatSection from "@/app/components/chat-section";
import LeftNav from "@/app/components/left-nav";
import RightNav from "@/app/components/right-nav";
import { cookies } from "next/headers";
import { ResponseThread } from "./service/thread-service";
import { Suspense } from "react";

async function getThreads(token: string): Promise<ResponseThread[]> {  
  const response = await fetch(`${process.env.NEXT_PUBLIC_BASE_URL}/api/threads`, {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });

  if (!response.ok) {
    return []
  }
  console.log("response.json(): ", response.json());

  return await response.json() as ResponseThread[];  
}

async function getUser(token: string){
  
  const response = await fetch(`${process.env.NEXT_PUBLIC_BASE_URL}/api/auth/me`, {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });
  if (!response.ok) {
      return null
  }

  return await response.json();  
}

export default async function Home() {
  const token = cookies().get('access_token');
  const threadData = token?.value ? await getThreads(token.value as string) : [];
  const userData = token?.value ? await getUser(token.value as string) : null;
  
  return (
      <main className="flex min-h-screen">
        <Suspense fallback={<div>Loading...</div>}>
          <LeftNav userThreads={threadData} userData={userData} />
          <ChatSection />
          <RightNav />
        </Suspense>
      </main>
  );
}
