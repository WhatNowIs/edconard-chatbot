import LeftNav from "@/app/components/left-nav";
import RightNav from "@/app/components/right-nav";
import AccountOverview from "@/app/components/ui/account/account-overview";
import UpdateProfile from "@/app/components/ui/account/update-profile";
import { ResponseThread } from "@/app/service/thread-service";
import { cookies } from "next/headers";
import { redirect } from "next/navigation";
import { Suspense } from "react";
import ChangePasswordForm from "../components/ui/account/change-password-form";
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
          <div className="grid w-full grid-cols-1 gap-y-10 px-4 py-16 sm:px-6 md:grid-cols-3 lg:px-8">
            <UpdateProfile user={userData.user as UserFormType} />
            <AccountOverview userData={userData.user as UserFormType} />
          </div>

          <div className="grid w-full grid-cols-1 gap-y-10 px-4 py-16 sm:px-6 md:grid-cols-3 lg:px-8">
            <div>
              <h2 className="text-base font-semibold leading-7">
                Change password
              </h2>
              <p className="mt-1 text-sm leading-6 text-gray-400">
                Update your password associated with your account.
              </p>
            </div>

            <ChangePasswordForm />
          </div>
        </main>
        <RightNav />
      </div>
    </Suspense>
  );
}
