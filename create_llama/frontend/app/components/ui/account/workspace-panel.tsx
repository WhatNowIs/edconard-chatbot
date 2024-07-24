import {
  addThreadToWorkspace,
  addUserToWorkspace,
  createWorkspace,
  fetchWorkspaces,
  removeThreadFromWorkspace,
  removeUserFromWorkspace,
  ResponseWorkspace,
} from "@/app/service/workspace-service";
import { useEffect, useState } from "react";
import WorkspaceCreationForm from "./workspace/create-form";
import ThreadManagement from "./workspace/thread-management";
import UserManagementForm from "./workspace/user-management";
import WorkspaceList from "./workspace/workspace-list";

// Define interfaces for the props of each component

export default function WorkspacePanel() {
  const [workspaceName, setWorkspaceName] = useState<string>("");
  const [userId, setUserId] = useState<string>("");
  const [threadId, setThreadId] = useState<string>("");
  const [workspaceId, setWorkspaceId] = useState<string>("");
  const [workspaces, setWorkspaces] = useState<ResponseWorkspace[]>([]);

  useEffect(() => {
    fetchWorkspacesList();
  }, []);

  const handleCreateWorkspace = async () => {
    try {
      await createWorkspace({ name: workspaceName });
      alert("Workspace created successfully");
      fetchWorkspacesList();
    } catch (error) {
      console.error("Error creating workspace:", error);
    }
  };

  const handleRemoveUser = async () => {
    try {
      await removeUserFromWorkspace(workspaceId, userId);
      alert("User removed successfully");
    } catch (error) {
      console.error("Error removing user:", error);
    }
  };

  const handleRemoveThread = async () => {
    try {
      await removeThreadFromWorkspace(workspaceId, threadId);
      alert("Thread removed successfully");
    } catch (error) {
      console.error("Error removing thread:", error);
    }
  };

  const handleAddUser = async () => {
    try {
      await addUserToWorkspace(workspaceId, userId);
      alert("User added successfully");
    } catch (error) {
      console.error("Error adding user:", error);
    }
  };

  const handleAddThread = async () => {
    try {
      await addThreadToWorkspace(workspaceId, threadId);
      alert("Thread added successfully");
    } catch (error) {
      console.error("Error adding thread:", error);
    }
  };

  const fetchWorkspacesList = async () => {
    try {
      const workspaces = await fetchWorkspaces();
      setWorkspaces(workspaces);
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
