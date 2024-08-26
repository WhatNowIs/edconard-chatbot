"use client";

import AuthContext from "@/app/context/auth-context";
import ChatContext from "@/app/context/chat-context";
import { UserFormType } from "@/app/service/user-service";
import {
  addUserToWorkspace,
  createWorkspace,
  fetchWorkspaces,
  removeUserFromWorkspace,
  ResponseWorkspace,
  UserManagementType,
  WorkspaceCreate,
} from "@/app/service/workspace-service";
import { useContext, useEffect } from "react";
import WorkspaceCreationForm from "./workspace/create-form";
import UserManagementForm from "./workspace/user-management";
import WorkspaceList from "./workspace/workspace-list";

// Define interfaces for the props of each component

export default function WorkspacePanel({
  workspaceData,
  users,
}: {
  workspaceData: ResponseWorkspace[];
  users: UserFormType[];
}) {
  const authContext = useContext(AuthContext);
  const chatContext = useContext(ChatContext);

  if (!authContext || !chatContext) {
    return <></>;
  }

  const { workspaces, setWorkspaces, setUsers } = chatContext;

  useEffect(() => {
    fetchWorkspacesList();
  }, []);

  const handleCreateWorkspace = async (data: WorkspaceCreate) => {
    try {
      await createWorkspace(data);
      alert("Workspace created successfully");
      fetchWorkspacesList();
    } catch (error) {
      console.error("Error creating workspace:", error);
    }
  };

  const handleRemoveUser = async (data: UserManagementType) => {
    try {
      await removeUserFromWorkspace(data.workspace_id, data.user_id);
      alert("User removed successfully");
    } catch (error) {
      console.error("Error removing user:", error);
    }
  };

  const handleAddUser = async (data: UserManagementType) => {
    try {
      await addUserToWorkspace(data.workspace_id, data.user_id);
      alert("User added successfully");
    } catch (error) {
      console.error("Error adding user:", error);
    }
  };

  const fetchWorkspacesList = async () => {
    try {
      const data = await fetchWorkspaces();

      setWorkspaces(data);

      return data;
    } catch (error) {
      console.error("Error fetching workspaces:", error);

      return [];
    }
  };

  useEffect(() => {
    setWorkspaces(workspaceData);
    setUsers(users);
  }, []);

  return (
    <>
      <div className="grid w-full grid-cols-1 gap-y-10 px-4 py-16 sm:px-6 md:grid-cols-1 lg:px-8">
        <WorkspaceCreationForm handleCreateWorkspace={handleCreateWorkspace} />
        <hr />
        <UserManagementForm
          handleAddUser={handleAddUser}
          handleRemoveUser={handleRemoveUser}
          fetchWorkspacesList={fetchWorkspacesList}
        />

        <hr />
        {/* <ThreadManagement
          handleAddThread={handleAddThread}
          handleRemoveThread={handleRemoveThread}
        />
        <hr /> */}
      </div>

      <div className="grid w-full grid-cols-1 gap-y-10 px-4 py-16 sm:px-6 lg:px-8">
        <WorkspaceList
          workspaces={workspaces}
          fetchWorkspacesList={fetchWorkspacesList}
        />
      </div>
    </>
  );
}
