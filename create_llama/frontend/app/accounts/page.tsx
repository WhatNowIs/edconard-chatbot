import LeftNav from "@/app/components/left-nav";
import RightNav from "@/app/components/right-nav";
import { ResponseThread } from "@/app/service/thread-service";
import { cookies } from "next/headers";
import { redirect } from "next/navigation";
import { Suspense } from "react";
import SettingsPanel from "../components/ui/account/settings-panel";
import {
  UserFormType,
  getChatMode,
  getUsersNotInWorkspace,
} from "../service/user-service";
import { getBackendURL } from "../service/utils";
import { ResponseWorkspace } from "../service/workspace-service";
import { UserRole } from "../utils/multi-mode-select";
import { decodeToken } from "../utils/shared";

async function getWorkspaces(token: string, options: RequestInit = {}) {
  const res = await fetch(`${getBackendURL()}/api/workspaces/`, {
    ...options,
    headers: {
      ...options.headers,
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
    },
  });

  if (!res.ok) {
    const error = JSON.parse(await res.text());
    throw new Error(error.detail);
  }

  return res.json();
}

async function getThreads(token: string): Promise<ResponseThread[]> {
  const threadResponse = await fetch(
    `${process.env.NEXT_PUBLIC_BASE_URL}/api/threads`,
    {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    },
  );
  if (!threadResponse.ok) {
    return [];
  }
  return (await threadResponse.json()) as ResponseThread[];
}

async function getUser(
  token: string,
): Promise<{ user: UserFormType | null; mode: boolean }> {
  const response = await fetch(
    `${process.env.NEXT_PUBLIC_BASE_URL}/api/auth/me`,
    {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    },
  );
  if (!response.ok) {
    return { user: null, mode: false };
  }
  const user = (await response.json()) as UserFormType;
  const { mode } = await getChatMode(user.id as string, token);

  return { user, mode };
}

export default async function AccountSettings() {
  const token = cookies().get("access_token");

  if (!token) {
    redirect("/signin");
  }

  const threadData = token.value ? await getThreads(token.value as string) : [];
  const userData = token?.value
    ? await getUser(token.value as string)
    : { user: null, mode: false };

  const decodedToken = decodeToken(token.value as string) as {
    email: string;
    sub: string;
    role: string;
  };

  let workspaces: ResponseWorkspace[] = [];
  let users: UserFormType[] = [];

  if (decodedToken.role === UserRole.SUPER_ADMIN) {
    workspaces = await getWorkspaces(token.value as string);

    const workspaceId = workspaces[0].id;

    const response = await getUsersNotInWorkspace(
      token.value as string,
      workspaceId,
    );

    users = response.status === 200 ? (response.data as UserFormType[]) : [];
  }

  return (
    <Suspense fallback={<div>Loading...</div>}>
      <div className="w-full flex h-screen">
        <LeftNav
          userThreads={threadData}
          userData={userData.user}
          mode={userData.mode}
        />
        <main className="w-full h-screen items-center flex flex-col overflow-auto">
          <SettingsPanel
            userData={userData.user as UserFormType}
            workspaces={workspaces}
            users={users}
          />
        </main>
        <RightNav />
      </div>
    </Suspense>
  );
}
