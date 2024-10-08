"use client";

/* eslint-disable @typescript-eslint/no-explicit-any */
import AuthContext from "@/app/context/auth-context";
import ChatContext from "@/app/context/chat-context";
import { UserSigninSchema, UserSigninType } from "@/app/service/user-service";
import { getAllWorkspaces } from "@/app/service/workspace-service";
import {
  decodeToken,
  getAccessToken,
  hasTokenExpired,
} from "@/app/utils/shared";
import { zodResolver } from "@hookform/resolvers/zod";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useContext, useEffect, useState } from "react";
import { useForm } from "react-hook-form";
import { SubmitButton } from "../custom/submitButton";
import { Form, FormControl, FormField, FormItem, FormLabel } from "../form";
import { Input } from "../input";
import { cn } from "../lib/utils";
import { Toaster } from "../toaster";
import { useToast } from "../use-toast";

export default function SigninForm() {
  const form = useForm({
    resolver: zodResolver(UserSigninSchema),
  });
  const { toast } = useToast();
  const router = useRouter();
  const [isSubmitting, setIsSubmitting] = useState<boolean>(false);
  const authContext = useContext(AuthContext);
  const chatContext = useContext(ChatContext);

  if (!authContext) {
    throw new Error("useContext must be used within an AuthProvider");
  }
  const { login } = authContext;

  const onSubmit = async (data: any) => {
    setIsSubmitting(true);
    try {
      const configData = await login(data as UserSigninType);
      if (configData.user !== null) {
        const workspaces = await getAllWorkspaces(getAccessToken());

        chatContext?.setWorkspaces(workspaces);

        router.push("/");
      } else {
        toast({
          className: cn(
            "top-0 right-0 flex fixed md:max-w-[420px] md:top-4 md:right-4 text-red-500",
          ),
          title: "Failed to login",
          description: configData.message,
        });
      }
    } catch (err) {
      console.error(err);
      toast({
        className: cn(
          "top-0 right-0 flex fixed md:max-w-[420px] md:top-4 md:right-4 text-red-500",
        ),
        title: "Failed to log in to the system",
      });
    }
    setIsSubmitting(false);
  };

  useEffect(() => {
    const decodedString = decodeToken(getAccessToken()) as any;

    if (!hasTokenExpired(decodedString)) {
      router.push("/");
    }
  }, []);

  return (
    <Form {...form}>
      <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4 mb-4">
        <FormField
          control={form.control}
          name="email"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Email address</FormLabel>
              <FormControl>
                <Input {...field} />
              </FormControl>
            </FormItem>
          )}
        />
        <FormField
          control={form.control}
          name="password"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Password</FormLabel>
              <FormControl>
                <Input type="password" {...field} />
              </FormControl>
            </FormItem>
          )}
        />
        <div className="flex items-center justify-between">
          <div className="flex items-center">
            <input
              id="remember-me"
              name="remember-me"
              type="checkbox"
              className="h-4 w-4 rounded border-gray-300 text-indigo-600 focus:ring-indigo-600"
            />
            <label
              htmlFor="remember-me"
              className="ml-3 block text-sm leading-6 text-gray-900"
            >
              Remember me
            </label>
          </div>
          <div className="text-sm leading-6">
            <Link
              href="/forgot-password"
              className="font-semibold text-secondary-foreground"
            >
              Forgot password?
            </Link>
          </div>
        </div>
        <SubmitButton
          isSubmitting={isSubmitting}
          text="Sign in"
          className="w-full flex items-center"
        />
        <Toaster />
      </form>
    </Form>
  );
}
