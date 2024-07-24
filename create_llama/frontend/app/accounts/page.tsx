import LeftNav from "@/app/components/left-nav";
import RightNav from "@/app/components/right-nav";
import { ResponseThread } from "@/app/service/thread-service";
import { cookies } from "next/headers";
import { redirect } from "next/navigation";
import { Suspense } from "react";
import SettingsPanel from "../components/ui/account/settings-panel";
import { UserFormType, getChatMode } from "../service/user-service";

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

  console.log(token);

  if (!token) {
    redirect("/signin");
  }

  const threadData = token.value ? await getThreads(token.value as string) : [];
  const userData = token?.value
    ? await getUser(token.value as string)
    : { user: null, mode: false };

  return (
    <Suspense fallback={<div>Loading...</div>}>
      <div className="w-full flex h-screen">
        <LeftNav
          userThreads={threadData}
          userData={userData.user}
          mode={userData.mode}
        />
        <main className="w-full h-screen items-center flex flex-col overflow-auto">
          <SettingsPanel userData={userData.user as UserFormType} />
        </main>
        <RightNav />
      </div>
    </Suspense>
  );
}
