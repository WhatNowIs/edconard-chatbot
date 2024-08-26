"use client";

import AuthContext from "@/app/context/auth-context";
import ChatContext, { SettingPanel } from "@/app/context/chat-context";
import { UserRole } from "@/app/utils/multi-mode-select";
import { useContext } from "react";
import { HiBriefcase, HiUserCircle } from "react-icons/hi2";

export default function OtherSettings() {
  const authContext = useContext(AuthContext);
  const chatContext = useContext(ChatContext);

  if (!authContext || !chatContext) {
    throw new Error(
      "useContext must be used within an AuthProvider and ChatProvider",
    );
  }
  const { user } = authContext;
  const { currentSettingPanel, setCurrentSettingPanel } = chatContext;

  const getIcon = (panel: SettingPanel) => {
    switch (panel) {
      case SettingPanel.Profile:
        return <HiUserCircle className="mr-2" />;
      case SettingPanel.Workspace:
        return <HiBriefcase className="mr-2" />;
      default:
        return null;
    }
  };

  return (
    <div className="mb-2 w-full">
      <div className="w-full flex flex-col justify-between items-center text-gray-700 mb-2">
        {Object.values(SettingPanel).map((panel) => {
          if (panel === "Workspaces") {
            if (user?.role?.name as string === UserRole.SUPER_ADMIN) {
              return (
                <div
                  key={panel}
                  className={`w-full flex items-center justify-left text-gray-800 text-sm my-2 cursor-pointer hover:bg-gray-100 hover:rounded-md p-2 ${
                    currentSettingPanel === panel
                      ? "bg-gray-100 rounded-md"
                      : ""
                  }`}
                  onClick={() => setCurrentSettingPanel(panel)}
                >
                  {getIcon(panel)}
                  <span>{panel}</span>
                </div>
              );
            } else {
              return null;
            }
          } else {
            return (
              <div
                key={panel}
                className={`w-full flex items-center justify-left text-gray-800 text-sm my-2 cursor-pointer hover:bg-gray-100 hover:rounded-md p-2 ${
                  currentSettingPanel === panel ? "bg-gray-100 rounded-md" : ""
                }`}
                onClick={() => setCurrentSettingPanel(panel)}
              >
                {getIcon(panel)}
                <span>{panel}</span>
              </div>
            );
          }
        })}
      </div>
    </div>
  );
}
