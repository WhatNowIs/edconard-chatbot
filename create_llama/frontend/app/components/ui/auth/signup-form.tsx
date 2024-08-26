"use client";

/* eslint-disable @typescript-eslint/no-explicit-any */
import {
  UserFormType,
  UserSchema,
  createUserAccount,
} from "@/app/service/user-service";
import { zodResolver } from "@hookform/resolvers/zod";
import { useRouter } from "next/navigation";
import { useState } from "react";
import { useForm } from "react-hook-form";
import { SubmitButton } from "../custom/submitButton";
import { Form, FormControl, FormField, FormItem, FormLabel } from "../form";
import { Input } from "../input";
import { cn } from "../lib/utils";
import { Toaster } from "../toaster";
import { useToast } from "../use-toast";

export default function SignupForm() {
  const form = useForm({
    resolver: zodResolver(UserSchema),
  });
  const { toast } = useToast();
  const router = useRouter();
  const [isSubmitting, setIsSubmitting] = useState<boolean>(false);

  const onSubmit = async (data: any) => {
    setIsSubmitting(true);
    // Send the data to the server
    try {
      const configData = await createUserAccount(data as UserFormType);

      if (configData.status === 200) router.push("/auth/verify-account-msg");
      else {
        toast({
          className: cn(
            "top-0 right-0 flex fixed md:max-w-[420px] md:top-4 md:right-4 text-red-500",
          ),
          title: "Failed to create account",
          description: configData.message,
        });
      }
    } catch (err) {
      console.error(err);
      toast({
        className: cn(
          "top-0 right-0 flex fixed md:max-w-[420px] md:top-4 md:right-4 text-red-500",
        ),
        title: "Failed to update config",
        description: "An error has occurred while creating your account",
      });
    }
    setIsSubmitting(false);
  };

  return (
    <Form {...form}>
      <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4 mb-4">
        <div className="flex gap-4">
          <FormField
            control={form.control}
            name="first_name"
            render={({ field }) => (
              <FormItem>
                <FormLabel>First name</FormLabel>
                <FormControl>
                  <Input {...field} />
                </FormControl>
              </FormItem>
            )}
          />
          <FormField
            control={form.control}
            name="last_name"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Last name</FormLabel>
                <FormControl>
                  <Input {...field} />
                </FormControl>
              </FormItem>
            )}
          />
        </div>
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
          name="phone_number"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Phone number</FormLabel>
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
        <SubmitButton
          isSubmitting={isSubmitting}
          text="Create"
          className="w-full flex items-center"
        />
      </form>
      <Toaster />
    </Form>
  );
}
