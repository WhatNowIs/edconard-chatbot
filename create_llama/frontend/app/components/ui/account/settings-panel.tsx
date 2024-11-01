"use client";

import AccountOverview from "@/app/components/ui/account/account-overview";
import AuthContext from "@/app/context/auth-context";
import ChatContext, { SettingPanel } from "@/app/context/chat-context";
import { UserFormType } from "@/app/service/user-service";
import { ResponseWorkspace } from "@/app/service/workspace-service";
import { UserRole } from "@/app/utils/multi-mode-select";
import { useContext } from "react";
import ChangePasswordForm from "./change-password-form";
import WorkspacePanel from "./workspace-panel";
import Accounts from "./workspace/user-accounts";

export default function SettingsPanel({
  users,
  userData,
  workspaces,
}: {
  users: UserFormType[];
  userData: UserFormType;
  workspaces: ResponseWorkspace[];
}) {
  const authContext = useContext(AuthContext);
  const chatContext = useContext(ChatContext);

  if (!authContext || !chatContext) {
    throw new Error(
      "useContext must be used within an AuthProvider and ChatProvider",
    );
  }
  const { user } = authContext;
  const { currentSettingPanel } = chatContext;

  const ProfilePanel = () => {
    return (
      <>
        <div className="grid w-full grid-cols-1 gap-y-10 px-4 py-16 sm:px-6 md:grid-cols-3 lg:px-8">
          {/* <UpdateProfile user={userData} /> */}
          <div></div>
          <AccountOverview userData={userData} />
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
      </>
    );
  };

  return (
    <>
      {currentSettingPanel === SettingPanel.Profile && <ProfilePanel />}
      {currentSettingPanel === SettingPanel.Accounts &&
        (user?.role?.name as string) === UserRole.SUPER_ADMIN && <Accounts />}
      {currentSettingPanel === SettingPanel.Workspace &&
        (user?.role?.name as string) === UserRole.SUPER_ADMIN && (
          <WorkspacePanel workspaceData={workspaces} users={users} />
        )}
    </>
  );
}
