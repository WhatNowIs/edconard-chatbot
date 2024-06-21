import { z } from "zod";
import { getBaseURL } from "./utils";

const ResponseMessageSchema = z.object({
    id: z.string(),
    thread_id: z.string(),
    user_id: z.string(),
    role: z.string(),
    content: z.string(),
    timestamp: z.string(),
    annotations: z.array(z.any())
});
  
const ResponseThreadSchema = z.object({
    id: z.string(),
    user_id: z.string(),
    title: z.string(),
    messages: z.array(ResponseMessageSchema),
});


const ThreadCreateSchema = z.object({
    user_id: z.string(),
    title: z.string(),
});


export type ResponseMessage = z.TypeOf<typeof ResponseMessageSchema>;
export type ResponseThread = z.TypeOf<typeof ResponseThreadSchema>;
export type ThreadCreate = z.TypeOf<typeof ThreadCreateSchema>;


const baseURL = `${getBaseURL()}/api/chat/threads`;

async function fetchWithAuth(url: string, options: RequestInit = {}) {  
  const access_token = localStorage.getItem('access_token');

  const res = await fetch(url, {
    ...options,
    headers: {
      ...options.headers,
      'Content-Type': 'application/json',
      Authorization: `Bearer ${access_token}`
    },
  });

  if (!res.ok) {
    const error = await res.text();
    throw new Error(error);
  }

  return res.json();
}

export async function createThread(data: ThreadCreate): Promise<ResponseThread> {
  const res = await fetchWithAuth(baseURL, {
    method: 'POST',
    body: JSON.stringify(data),
  });
  return res as ResponseThread;
}

export async function fetchThreads(): Promise<ResponseThread[]> {
  const res = await fetchWithAuth(baseURL);
  return res as ResponseThread[];
}

export async function updateThread(thread_id: string, data: ThreadCreate): Promise<ResponseThread> {
  const res = await fetchWithAuth(`${baseURL}/${thread_id}`, {
    method: 'PATCH',
    body: JSON.stringify(data),
  });
  return res as ResponseThread;
}

export async function getThread(thread_id: string): Promise<ResponseThread> {
  const res = await fetchWithAuth(`${baseURL}/${thread_id}`);
  return res as ResponseThread;
}

export async function getMessagesByThreadId(thread_id: string): Promise<ResponseMessage[]> {
  const res = await fetchWithAuth(`${baseURL}/messages/${thread_id}`);
  return res as ResponseMessage[];
}

export async function removeThread(thread_id: string): Promise<{ message: string }> {
  const res = await fetchWithAuth(`${baseURL}/${thread_id}`, {
    method: 'DELETE',
  });
  return res as { message: string };
}
