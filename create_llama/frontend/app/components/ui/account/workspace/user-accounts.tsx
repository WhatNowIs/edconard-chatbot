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

import AuthContext from "@/app/context/auth-context";
import { getAccessToken } from "@/app/utils/shared";
import { cn } from "../../lib/utils";
import { useToast } from "../../use-toast";
import UserInfoForm from "./user-info";

interface UserManagementFormProps {
  handleAddUser: (data: UserManagementType) => Promise<void>;
  handleRemoveUser: (data: UserManagementType) => Promise<void>;
  fetchWorkspacesList: () => Promise<ResponseWorkspace[]>;
}

export const Accounts = () => {
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

  const { setUsers, users, currentUser, setCurrentUser } = authContext;

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
      // await handleRemoveUser(data);
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
        title: "Failed to remove user.",
      });
    }
  };

  const UserCard = ({ user }: { user: UserFormType }) => {
    const onUserSelect = (user: UserFormType) => {
      console.log(user);
      setCurrentUser(user);
    };
    return (
      <div
        onClick={() => onUserSelect(user)}
        className={`w-2/3 flex items-center p-2 shadow-sm cursor-pointer hover:bg-gray-100 active:bg-gray-100 rounded-lg ${
          currentUser?.id === user.id ? "bg-gray-100" : "bg-white"
        }`}
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

    console.log(users);
  }, []);

  return (
    <div className="w-full h-screen p-4 grid grid-cols-2 gap-4">
      <div className="col-span-1 h-screen overflow-y-auto">
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

      <div className="col-span-1 h-screen">
        {currentUser && <UserInfoForm user={currentUser} />}
      </div>
    </div>
  );
};

export default Accounts;
