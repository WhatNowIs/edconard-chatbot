"use client";

import AuthContext from "@/app/context/auth-context";
import ChatContext from "@/app/context/chat-context";
import {
  addThreadToWorkspace,
  addUserToWorkspace,
  createWorkspace,
  fetchWorkspaces,
  removeThreadFromWorkspace,
  removeUserFromWorkspace,
  WorkspaceCreate,
} from "@/app/service/workspace-service";
import { useContext, useEffect } from "react";
import WorkspaceCreationForm from "./workspace/create-form";
import ThreadManagement from "./workspace/thread-management";
import UserManagementForm from "./workspace/user-management";
import WorkspaceList from "./workspace/workspace-list";

// Define interfaces for the props of each component

export default function WorkspacePanel() {
  const authContext = useContext(AuthContext);
  const chatContext = useContext(ChatContext);

  if (!authContext || !chatContext) {
    return <></>;
  }

  const { user } = authContext;
  const { currentWorkspace, workspaces, setWorkspaces } = chatContext;

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

  const handleRemoveUser = async () => {
    try {
      await removeUserFromWorkspace(
        currentWorkspace?.id as string,
        user?.id as string,
      );
      alert("User removed successfully");
    } catch (error) {
      console.error("Error removing user:", error);
    }
  };

  const handleRemoveThread = async () => {
    try {
      await removeThreadFromWorkspace(
        currentWorkspace?.id as string,
        "threadId",
      );
      alert("Thread removed successfully");
    } catch (error) {
      console.error("Error removing thread:", error);
    }
  };

  const handleAddUser = async () => {
    try {
      await addUserToWorkspace(
        currentWorkspace?.id as string,
        user?.id as string,
      );
      alert("User added successfully");
    } catch (error) {
      console.error("Error adding user:", error);
    }
  };

  const handleAddThread = async () => {
    try {
      await addThreadToWorkspace(currentWorkspace?.id as string, "threadId");
      alert("Thread added successfully");
    } catch (error) {
      console.error("Error adding thread:", error);
    }
  };

  const fetchWorkspacesList = async () => {
    try {
      const data = await fetchWorkspaces();

      setWorkspaces(data);
    } catch (error) {
      console.error("Error fetching workspaces:", error);
    }
  };

  return (
    <>
      <div className="grid w-full grid-cols-1 gap-y-10 px-4 py-16 sm:px-6 md:grid-cols-1 lg:px-8">
        <WorkspaceCreationForm handleCreateWorkspace={handleCreateWorkspace} />
        <hr />
        <UserManagementForm
          handleAddUser={handleAddUser}
          handleRemoveUser={handleRemoveUser}
        />

        <hr />
        <ThreadManagement
          handleAddThread={handleAddThread}
          handleRemoveThread={handleRemoveThread}
        />
        <hr />
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
