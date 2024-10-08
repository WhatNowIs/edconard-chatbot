import ChatSection from "@/app/components/chat-section";
import LeftNav from "@/app/components/left-nav";
import RightNav from "@/app/components/right-nav";
import SkeletonRightNav, {
  SkeletonChatSection,
  SkeletonLeftNav,
} from "@/app/components/suspense/suspense-chat-section";
import { cookies } from "next/headers";
import { Suspense } from "react";
import { ResponseThread } from "./service/thread-service";
import { UserFormType, getChatMode } from "./service/user-service";
import { getBackendURL } from "./service/utils";
import { getAllWorkspaces } from "./service/workspace-service";

async function getThreads(token: string): Promise<ResponseThread[]> {
  const response = await fetch(`${getBackendURL()}/api/threads`, {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });

  if (!response.ok) {
    return [];
  }

  return (await response.json()) as ResponseThread[];
}

async function getUser(
  token: string,
): Promise<{ user: UserFormType | null; mode: boolean | null }> {
  const response = await fetch(
    `${process.env.NEXT_PUBLIC_BASE_URL}/api/auth/me`,
    {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    },
  );
  if (!response.ok) {
    return { user: null, mode: null };
  }

  const user = (await response.json()) as UserFormType;

  const { mode } = await getChatMode(user.id as string, token);

  return { user, mode };
}

export default async function Home() {
  const token = cookies().get("access_token");
  const threadData = token?.value
    ? await getThreads(token.value as string)
    : [];
  const userData = token?.value
    ? await getUser(token.value as string)
    : { user: null, mode: null };

  const workspaces = token?.value
    ? await getAllWorkspaces(token?.value as string)
    : [];

  return (
    <main className="flex min-h-screen">
      <Suspense fallback={<SkeletonLeftNav />}>
        <LeftNav
          userThreads={threadData}
          userData={userData.user}
          mode={userData.mode !== null ? userData.mode : false}
        />
      </Suspense>
      <Suspense fallback={<SkeletonChatSection />}>
        <ChatSection workspaces={workspaces} />
      </Suspense>
      <Suspense fallback={<SkeletonRightNav />}>
        <RightNav />
      </Suspense>
    </main>
  );
}
