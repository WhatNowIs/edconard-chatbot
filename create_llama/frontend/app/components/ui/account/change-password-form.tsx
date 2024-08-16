"use client";

/* eslint-disable @typescript-eslint/no-explicit-any */
import {
  changePassword,
  ChangePasswordSchema,
  ChangePasswordType,
} from "@/app/service/user-service";
import { zodResolver } from "@hookform/resolvers/zod";
import { useRouter } from "next/navigation";
import { useState } from "react";
import { useForm } from "react-hook-form";
import { SubmitButton } from "../custom/submitButton";
import { Form, FormControl, FormField, FormItem, FormLabel } from "../form";
import { Input } from "../input";
import { cn } from "../lib/utils";
import { useToast } from "../use-toast";

export default function ChangePasswordForm() {
  const form = useForm({
    resolver: zodResolver(ChangePasswordSchema),
  });
  const { toast } = useToast();
  const router = useRouter();
  const [isSubmitting, setIsSubmitting] = useState<boolean>(false);

  const onSubmit = async (data: any) => {
    setIsSubmitting(true);
    // Send the data to the server
    try {
      const response = await changePassword(data as ChangePasswordType);

      if (response.status === 200) {
        toast({
          className: cn(
            "top-0 right-0 flex fixed md:max-w-[420px] md:top-4 md:right-4 text-green-500",
          ),
          description: "Password changed successfully",
        });
        router.refresh();
        form.setValue("current_password", "");
        form.setValue("new_password", "");
        form.setValue("confirm_password", "");
      } else {
        toast({
          className: cn(
            "top-0 right-0 flex fixed md:max-w-[420px] md:top-4 md:right-4 text-red-500",
          ),
          title: "Failed to change password",
        });
      }
    } catch (err) {
      console.error(err);
      toast({
        className: cn(
          "top-0 right-0 flex fixed md:max-w-[420px] md:top-4 md:right-4 text-red-500",
        ),
        title: "Failed to change password",
      });
    }
    setIsSubmitting(false);
  };

  return (
    <div className="md:col-span-2">
      <Form {...form}>
        <form
          onSubmit={form.handleSubmit(onSubmit)}
          className="w-full space-y-4 mb-4 grid grid-cols-1 gap-x-6 gap-y-3 sm:max-w-xl sm:grid-cols-3"
        >
          <FormField
            control={form.control}
            name="current_password"
            render={({ field }) => (
              <FormItem className="sm:col-span-3">
                <FormLabel>Current Password</FormLabel>
                <FormControl>
                  <Input type="password" {...field} />
                </FormControl>
              </FormItem>
            )}
          />
          <FormField
            control={form.control}
            name="new_password"
            render={({ field }) => (
              <FormItem className="sm:col-span-3">
                <FormLabel>New Password</FormLabel>
                <FormControl>
                  <Input type="password" {...field} />
                </FormControl>
              </FormItem>
            )}
          />
          <FormField
            control={form.control}
            name="confirm_password"
            render={({ field }) => (
              <FormItem className="sm:col-span-3">
                <FormLabel>Confirm Password</FormLabel>
                <FormControl>
                  <Input type="password" {...field} />
                </FormControl>
              </FormItem>
            )}
          />
          <SubmitButton
            isSubmitting={isSubmitting}
            text="Change Password"
            className="flex items-center"
          />
        </form>
      </Form>
    </div>
  );
}
