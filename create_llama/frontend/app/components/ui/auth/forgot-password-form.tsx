"use client";
/* eslint-disable @typescript-eslint/no-explicit-any */
import {
  ForgotPasswordSchema,
  ForgotPasswordType,
  forgotPassword,
} from "@/app/service/user-service";
import { zodResolver } from "@hookform/resolvers/zod";
import { useRouter } from "next/navigation";
import { useState } from "react";
import { useForm } from "react-hook-form";
import { SubmitButton } from "../custom/submitButton";
import { Form, FormControl, FormField, FormItem } from "../form";
import { Input } from "../input";

export default function ForgotPasswordForm() {
  const [isSubmitting, setIsSubmitting] = useState<boolean>(false);
  const form = useForm({
    resolver: zodResolver(ForgotPasswordSchema),
  });
  const router = useRouter();

  const forgot = async (data: any) => {
    const response = await forgotPassword(data as ForgotPasswordType);
    if (response.message) {
      router.push("/auth/reset-password-msg");
    }
    setIsSubmitting(false);
  };

  const onSubmit = (data: any) => {
    setIsSubmitting(true);
    forgot(data).catch((error) => console.log(error));
  };

  return (
    <Form {...form}>
      <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4 mb-4">
        <FormField
          control={form.control}
          name="email"
          render={({ field }) => (
            <FormItem>
              <FormControl>
                <Input {...field} placeholder="Your email" />
              </FormControl>
            </FormItem>
          )}
        />
        <div className="space-y-6">
          <SubmitButton
            isSubmitting={isSubmitting}
            text="Submit"
            className="w-full flex items-center"
          />
        </div>
      </form>
    </Form>
  );
}
