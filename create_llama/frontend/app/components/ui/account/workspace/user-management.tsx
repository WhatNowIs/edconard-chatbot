"use client";

import ChatContext from "@/app/context/chat-context";
import {
  ResponseWorkspace,
  UserManagementSchema,
  UserManagementType,
} from "@/app/service/workspace-service";
import { zodResolver } from "@hookform/resolvers/zod";
import { useContext } from "react";
import { useForm } from "react-hook-form";
import { SubmitButton } from "../../custom/submitButton";
import { Form, FormControl, FormField, FormItem } from "../../form";
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
  const { toast } = useToast();
  const form = useForm<UserManagementType>({
    resolver: zodResolver(UserManagementSchema),
  });

  const chatContext = useContext(ChatContext);

  if (!chatContext) return <></>;

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
      await handleRemoveUser(data);
      toast({
        className: cn(
          "top-0 right-0 flex fixed md:max-w-[420px] md:top-4 md:right-4 text-green-500",
        ),
        title: "User removed successfully",
      });
    } catch (error) {
      toast({
        className: cn(
          "top-0 right-0 flex fixed md:max-w-[420px] md:top-4 md:right-4 text-red-500",
        ),
        title: "Failed to remove user",
      });
    }
  };

  const onWorkspaceSelect = (value: string) => {
    form.setValue("workspace_id", value);
  };
  const onUserSelect = (value: string) => {
    form.setValue("user_id", value);
  };

  return (
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
                <Select onValueChange={onWorkspaceSelect} value={field.value}>
                  <SelectTrigger>
                    <SelectValue placeholder="Select a workspace" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectGroup>
                      <SelectLabel>Workspaces</SelectLabel>
                      {chatContext.workspaces.map((workspace) => (
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
      <form
        onSubmit={form.handleSubmit(onSubmitRemove)}
        className="w-full space-y-4 mb-4 grid grid-cols-1 gap-x-6 gap-y-3 sm:max-w-xl sm:grid-cols-3"
      >
        <SubmitButton
          isSubmitting={form.formState.isSubmitting}
          text="Remove User"
          className="flex items-center"
        />
      </form>
    </Form>
  );
};

export default UserManagementForm;
