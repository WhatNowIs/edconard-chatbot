"use client";

import ChatContext from "@/app/context/chat-context";
import { getAllUsers, UserFormType } from "@/app/service/user-service";
import {
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

import AuthContext from "@/app/context/auth-context";
import { getAccessToken } from "@/app/utils/shared";
import { cn } from "../../lib/utils";
import { useToast } from "../../use-toast";

interface UserManagementFormProps {
  handleAddUser: (data: UserManagementType) => Promise<void>;
  handleRemoveUser: (data: UserManagementType) => Promise<void>;
  fetchWorkspacesList: () => Promise<ResponseWorkspace[]>;
}

export const Accounts = ({
  handleAddUser,
  handleRemoveUser,
}: UserManagementFormProps) => {
  const [isWorkspaceUsersFetching, setIsWorkspaceUsersFetching] =
    useState<boolean>(false);
  const [isDeleting, setIsDeleting] = useState<boolean>(false);
  const { toast } = useToast();
  const form = useForm<UserManagementType>({
    resolver: zodResolver(UserManagementSchema),
  });

  const chatContext = useContext(ChatContext);
  const authContext = useContext(AuthContext);

  if (!chatContext || !authContext) return <></>;

  const { setUsers, users } = authContext;

  // const onSubmitAdd = async (data: UserManagementType) => {
  //   try {
  //     await handleAddUser(data);
  //     toast({
  //       className: cn(
  //         "top-0 right-0 flex fixed md:max-w-[420px] md:top-4 md:right-4 text-green-500",
  //       ),
  //       title: "User added successfully",
  //     });
  //   } catch (error) {
  //     toast({
  //       className: cn(
  //         "top-0 right-0 flex fixed md:max-w-[420px] md:top-4 md:right-4 text-red-500",
  //       ),
  //       title: "Failed to add user",
  //     });
  //   }
  // };

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

  const UserCard = ({ user }: { user: UserFormType }) => {
    const onUserSelect = (user: UserFormType) => {
      console.log(user);
    };
    return (
      <div
        onClick={() => onUserSelect(user)}
        className="w-96 flex items-center p-2 bg-white shadow-md hover:bg-slate-100 active:bg-slate-100 rounded-lg"
      >
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

  useEffect(() => {
    if (users.length === 0) {
      const fetchUsers = async () => {
        const result = await getAllUsers(getAccessToken());

        if (result.status === 200) setUsers(result.data);
        else {
          toast({
            className: cn(
              "top-0 right-0 flex fixed md:max-w-[420px] md:top-4 md:right-4 text-red-500",
            ),
            title: "Failed to fetch data",
            description:
              "An error has occurred while fetching users, please try to refresh the page.",
          });
        }
      };

      fetchUsers().catch((error) => console.log(error));
    }
  }, []);

  return (
    <div className="w-full grid grid-cols-2 gap-6">
      <div className="col-span-1 h-full overflow-y-auto">
        <div className="flex gap-6">
          <h2 className="mb-2">Users</h2>
        </div>
        <div className="grid grid-cols-1 gap-6">
          {!isWorkspaceUsersFetching ? (
            users.map((user: UserFormType) => (
              <UserCard key={user.id} user={user} />
            ))
          ) : (
            <Loader2 className="h-4 w-4 animate-spin" />
          )}
        </div>
      </div>
    </div>
  );
};

export default Accounts;
