"use client";

import ChatContext from "@/app/context/chat-context";
import { UserFormType } from "@/app/service/user-service";
import {
  getUsers,
  ResponseWorkspace,
  UserManagementSchema,
  UserManagementType,
} from "@/app/service/workspace-service";
import { zodResolver } from "@hookform/resolvers/zod";
import { Loader2 } from "lucide-react";
import Image from "next/image";
import { useContext, useEffect, useState } from "react";
import { useForm } from "react-hook-form";
import { HiOutlineTrash } from "react-icons/hi2";
import { SubmitButton } from "../../custom/submitButton";
import { Form, FormControl, FormField, FormItem } from "../../form";

import { getUsersNotInWorkspace } from "@/app/service/user-service";
import { getAccessToken } from "@/app/utils/shared";
import { cn } from "../../lib/utils";
import {
  Select,
  SelectContent,
  SelectGroup,
  SelectItem,
  SelectLabel,
  SelectTrigger,
  SelectValue,
} from "../../select";
import { useToast } from "../../use-toast";

interface UserManagementFormProps {
  handleAddUser: (data: UserManagementType) => Promise<void>;
  handleRemoveUser: (data: UserManagementType) => Promise<void>;
  fetchWorkspacesList: () => Promise<ResponseWorkspace[]>;
}

export const UserManagementForm = ({
  handleAddUser,
  handleRemoveUser,
}: UserManagementFormProps) => {
  const [isWorkspaceUserFetching, setIsWorkspaceUserFetching] =
    useState<boolean>(false);
  const [isDeleting, setIsDeleting] = useState<boolean>(false);
  const { toast } = useToast();
  const form = useForm<UserManagementType>({
    resolver: zodResolver(UserManagementSchema),
  });

  const chatContext = useContext(ChatContext);

  if (!chatContext) return <></>;

  const { workspaceUsers, setWorkspaceUsers, workspaces, setUsers } =
    chatContext;

  const onSubmitAdd = async (data: UserManagementType) => {
    try {
      await handleAddUser(data);
      toast({
        className: cn(
          "top-0 right-0 flex fixed md:max-w-[420px] md:top-4 md:right-4 text-green-500",
        ),
        title: "User added successfully",
      });
    } catch (error) {
      toast({
        className: cn(
          "top-0 right-0 flex fixed md:max-w-[420px] md:top-4 md:right-4 text-red-500",
        ),
        title: "Failed to add user",
      });
    }
  };

  const onSubmitRemove = async (data: UserManagementType) => {
    try {
      setIsDeleting(true);
      await handleRemoveUser(data);
      toast({
        className: cn(
          "top-0 right-0 flex fixed md:max-w-[420px] md:top-4 md:right-4 text-green-500",
        ),
        title: "User removed successfully",
      });
      setIsDeleting(false);
    } catch (error) {
      toast({
        className: cn(
          "top-0 right-0 flex fixed md:max-w-[420px] md:top-4 md:right-4 text-red-500",
        ),
        title: "Failed to remove user",
      });
    }
  };

  const onWorkspaceSelect = (workspaceIdValue: string) => {
    form.setValue("workspace_id", workspaceIdValue);

    const getWorkspaceUsers = async (value: string) => {
      setIsWorkspaceUserFetching(true);
      const [result, resultUsers] = await Promise.all([
        getUsers(value),
        getUsersNotInWorkspace(getAccessToken(), value),
      ]);

      const updatedUsers =
        resultUsers.status === 200 ? (resultUsers.data as UserFormType[]) : [];

      setWorkspaceUsers(result);
      setUsers(updatedUsers);
      setIsWorkspaceUserFetching(false);

      return;
    };

    if (workspaceIdValue) {
      getWorkspaceUsers(workspaceIdValue).catch((error) => console.log(error));
    }
  };

  const onUserSelect = (value: string) => {
    form.setValue("user_id", value);
  };

  useEffect(() => {
    if (workspaces.length > 0 && !form.getValues().workspace_id) {
      form.setValue("workspace_id", workspaces[0]?.id as string);
    }
  }, []);

  const UserCard = ({ user }: { user: UserFormType }) => {
    return (
      <div className="w-96 flex items-center p-2 bg-white shadow-md rounded-lg">
        <Image
          className="rounded-full"
          width={30}
          height={30}
          alt={`${user.first_name}'s avatar`}
          src="https://via.placeholder.com/40"
        />
        <div className="w-full ml-4">
          <h4 className="text-lg font-semibold">
            {user.first_name} {user.last_name}
          </h4>
          <p className="text-xs text-gray-500">{user.email}</p>
          <p className="text-xs text-gray-700">{user?.role?.name as string}</p>
        </div>{" "}
        <div className="w-6">
          <button
            type="button"
            disabled={isDeleting}
            className="w-6 h-full bg-none border-none hover:cursor-pointer"
            onClick={() =>
              onSubmitRemove({
                workspace_id: form.getValues().workspace_id,
                user_id: user.id as string,
              }).catch((error) => console.log(error))
            }
          >
            <HiOutlineTrash className="w-5 h-5 rounded-md text-slate-700 hover:text-slate-900" />
          </button>
        </div>
      </div>
    );
  };

  return (
    <div className="w-full grid grid-cols-3 gap-6">
      <div className="col-span-1">
        <Form {...form}>
          <form
            onSubmit={form.handleSubmit(onSubmitAdd)}
            className="w-full space-y-4 mb-4 grid grid-cols-1 gap-x-6 gap-y-3 sm:max-w-xl sm:grid-cols-3"
          >
            <FormField
              control={form.control}
              name="workspace_id"
              render={({ field }) => (
                <FormItem className="sm:col-span-3">
                  <FormControl>
                    <Select
                      onValueChange={onWorkspaceSelect}
                      value={field.value}
                    >
                      <SelectTrigger>
                        <SelectValue placeholder="Select a workspace" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectGroup>
                          <SelectLabel>Workspaces</SelectLabel>
                          {workspaces.map((workspace) => (
                            <SelectItem key={workspace.id} value={workspace.id}>
                              {workspace.name}
                            </SelectItem>
                          ))}
                        </SelectGroup>
                      </SelectContent>
                    </Select>
                  </FormControl>
                </FormItem>
              )}
            />
            <FormField
              control={form.control}
              name="user_id"
              render={({ field }) => (
                <FormItem className="sm:col-span-3">
                  <FormControl>
                    <Select onValueChange={onUserSelect} value={field.value}>
                      <SelectTrigger>
                        <SelectValue placeholder="Choose a user" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectGroup>
                          <SelectLabel>Users</SelectLabel>
                          {chatContext.users.map((user) => (
                            <SelectItem key={user.id} value={user.id as string}>
                              {user.first_name} {user.last_name} - {user.email}
                            </SelectItem>
                          ))}
                        </SelectGroup>
                      </SelectContent>
                    </Select>
                  </FormControl>
                </FormItem>
              )}
            />
            <SubmitButton
              isSubmitting={form.formState.isSubmitting}
              text="Add User"
              className="flex items-center"
            />
          </form>
        </Form>
      </div>

      <div className="col-span-2 h-[400px] overflow-y-auto">
        <div className="flex gap-6">
          <h2 className="mb-2">Current workspace users</h2>
        </div>
        <div className="grid grid-cols-1 gap-6">
          {!isWorkspaceUserFetching ? (
            workspaceUsers.map((workspaceUser) => (
              <UserCard key={workspaceUser.id} user={workspaceUser} />
            ))
          ) : (
            <Loader2 className="h-4 w-4 animate-spin" />
          )}
        </div>
      </div>
    </div>
  );
};

export default UserManagementForm;
