"use client";

import { ResponseWorkspace } from "@/app/service/workspace-service";

interface WorkspaceListProps {
  workspaces: ResponseWorkspace[];
  fetchWorkspacesList: () => Promise<ResponseWorkspace[]>;
}

export const WorkspaceList = ({
  workspaces,
  fetchWorkspacesList,
}: WorkspaceListProps) => {
  return (
    <div className="p-4 bg-white">
      <h2 className="text-lg font-semibold mb-2">Workspace List</h2>
      <button
        onClick={fetchWorkspacesList}
        className="mb-2 py-2 px-4 bg-blue-500 text-white rounded-md hover:bg-blue-600"
      >
        Refresh List
      </button>
      <ul className="mt-4">
        {workspaces.map((workspace) => (
          <li key={workspace.id} className="py-2 border-b">
            {workspace.name} (ID: {workspace.id})
          </li>
        ))}
      </ul>
    </div>
  );
};

export default WorkspaceList;
