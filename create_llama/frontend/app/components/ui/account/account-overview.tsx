"use client";

import AuthContext from "@/app/context/auth-context";
import { UserFormType } from "@/app/service/user-service";
import { useContext } from "react";
import { Button } from "../button";
import { Input } from "../input";

export default function AccountOverview({
  userData,
}: {
  userData: UserFormType;
}) {
  const authContext = useContext(AuthContext);

  if (!authContext) {
    throw new Error("useContext must be used within an AuthProvider");
  }
  const { user, setUser } = authContext;

  if (!user) {
    setUser(userData);
  }

  return (
    <form className="md:col-span-2">
      <h1 className="md:col-span-1 text-gray-800 text-3xl">Account Settings</h1>
      <div className="grid grid-cols-1 gap-x-6 gap-y-8 sm:max-w-xl sm:grid-cols-6 my-6">
        <div className="sm:col-span-3">
          <label
            htmlFor="first-name"
            className="block text-sm font-medium leading-6 "
          >
            First name
          </label>
          <div className="mt-2">
            <Input
              autoFocus
              name="message"
              placeholder="First name"
              className="flex-1"
              value={user?.first_name}
            />
          </div>
        </div>

        <div className="sm:col-span-3">
          <label
            htmlFor="last-name"
            className="block text-sm font-medium leading-6 "
          >
            Last name
          </label>
          <div className="mt-2">
            <Input
              autoFocus
              name="message"
              placeholder="Last name"
              className="flex-1"
              value={user?.last_name}
            />
          </div>
        </div>

        <div className="col-span-full">
          <label
            htmlFor="email"
            className="block text-sm font-medium leading-6"
          >
            Email address
          </label>
          <div className="mt-2">
            <Input
              type="email"
              disabled
              autoFocus
              name="message"
              placeholder="Email address"
              className="flex-1"
              value={user?.email}
            />
          </div>
        </div>
        <div className="col-span-full">
          <label
            htmlFor="email"
            className="block text-sm font-medium leading-6"
          >
            Phone Number
          </label>
          <div className="mt-2">
            <Input
              type="tel"
              autoFocus
              name="phone_number"
              placeholder="Email address"
              className="flex-1"
              value={user?.phone_number}
            />
          </div>
        </div>
        <div className="col-span-full">
          <label
            htmlFor="email"
            className="block text-sm font-medium leading-6"
          >
            Account Type
          </label>
          <div className="mt-2">
            <Input
              autoFocus
              disabled
              name="role"
              className="flex-1"
              value={user?.role?.name}
            />
          </div>
        </div>
      </div>

      <div className="mt-8 flex">
        <Button>Save</Button>
      </div>
    </form>
  );
}
