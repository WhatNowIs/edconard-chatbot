import { z } from "zod";
import { getCookie } from "./user-service";
import { getBackendURL } from "./utils";

export const UserManagementSchema = z.object({
  workspace_id: z.string().min(1, "Workspace ID is required"),
  user_id: z.string().min(1, "User ID is required"),
});

export const ThreadManagementSchema = z.object({
  workspace_id: z.string().min(1, "Workspace ID is required"),
  thread_id: z.string().min(1, "Thread ID is required"),
});

export const ResponseWorkspaceSchema = z.object({
  id: z.string(),
  name: z.string(),
  created_at: z.string(),
  updated_at: z.string().nullable(),
  status: z.string().nullable(),
  users: z.array(z.any()).optional(),
  threads: z.array(z.any()).optional(),
});

export const WorkspaceCreateSchema = z.object({
  name: z.string(),
});

export type ResponseWorkspace = z.TypeOf<typeof ResponseWorkspaceSchema>;
export type WorkspaceCreate = z.TypeOf<typeof WorkspaceCreateSchema>;
export type UserManagementType = z.infer<typeof UserManagementSchema>;
export type ThreadManagementType = z.infer<typeof ThreadManagementSchema>;

const baseURL = `${getBackendURL()}/api/workspaces/`;

async function fetchWithAuth(url: string, options: RequestInit = {}) {
  const access_token =
    localStorage.getItem("access_token") || getCookie("access_token");

  const res = await fetch(url, {
    ...options,
    headers: {
      ...options.headers,
      "Content-Type": "application/json",
      Authorization: `Bearer ${access_token}`,
    },
  });

  if (!res.ok) {
    const error = JSON.parse(await res.text());
    throw new Error(error.detail);
  }

  return res.json();
}

export async function createWorkspace(
  data: WorkspaceCreate,
): Promise<ResponseWorkspace> {
  const res = await fetchWithAuth(baseURL, {
    method: "POST",
    body: JSON.stringify(data),
  });
  return res as ResponseWorkspace;
}

export async function fetchWorkspaces(): Promise<ResponseWorkspace[]> {
  const res = await fetchWithAuth(baseURL);
  return res as ResponseWorkspace[];
}

export async function getAllWorkspaces(
  access_token: string,
): Promise<ResponseWorkspace[]> {
  const res = await fetch(baseURL, {
    method: "GET",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${access_token}`,
    },
  });

  if (!res.ok) {
    return [];
  }

  return (await res.json()) as ResponseWorkspace[];
}

export async function fetchWorkspacesByUser(
  userId: string,
): Promise<ResponseWorkspace[]> {
  const res = await fetchWithAuth(`${baseURL}user/${userId}`);
  return res as ResponseWorkspace[];
}

export async function updateWorkspace(
  workspace_id: string,
  data: WorkspaceCreate,
): Promise<ResponseWorkspace> {
  const res = await fetchWithAuth(`${baseURL}${workspace_id}`, {
    method: "PATCH",
    body: JSON.stringify(data),
  });
  return res as ResponseWorkspace;
}

export async function getWorkspace(
  workspace_id: string,
): Promise<ResponseWorkspace> {
  const res = await fetchWithAuth(`${baseURL}${workspace_id}`);
  return res as ResponseWorkspace;
}

export async function addUserToWorkspace(
  workspace_id: string,
  user_id: string,
): Promise<ResponseWorkspace> {
  const res = await fetchWithAuth(
    `${baseURL}${workspace_id}/users/${user_id}`,
    {
      method: "POST",
    },
  );
  return res as ResponseWorkspace;
}

export async function removeUserFromWorkspace(
  workspace_id: string,
  user_id: string,
): Promise<ResponseWorkspace> {
  const res = await fetchWithAuth(
    `${baseURL}${workspace_id}/users/${user_id}`,
    {
      method: "POST",
      body: JSON.stringify({ user_id }),
    },
  );
  return res as ResponseWorkspace;
}

export async function addThreadToWorkspace(
  workspace_id: string,
  thread_id: string,
): Promise<ResponseWorkspace> {
  const res = await fetchWithAuth(`${baseURL}${workspace_id}/add_thread`, {
    method: "POST",
    body: JSON.stringify({ thread_id }),
  });
  return res as ResponseWorkspace;
}

export async function removeThreadFromWorkspace(
  workspace_id: string,
  thread_id: string,
): Promise<ResponseWorkspace> {
  const res = await fetchWithAuth(`${baseURL}${workspace_id}/remove_thread`, {
    method: "POST",
    body: JSON.stringify({ thread_id }),
  });
  return res as ResponseWorkspace;
}

export async function removeWorkspace(
  workspace_id: string,
): Promise<{ message: string }> {
  const res = await fetchWithAuth(`${baseURL}${workspace_id}`, {
    method: "DELETE",
  });
  return res as { message: string };
}
