"use client";

/* eslint-disable @typescript-eslint/no-explicit-any */
import {
  ResetPasswordFormSchema,
  resetPassword,
} from "@/app/service/user-service";
import base64ToString from "@/app/utils/shared";
import { zodResolver } from "@hookform/resolvers/zod";
import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { useForm } from "react-hook-form";
import { Button } from "../button";
import { Form, FormControl, FormField, FormItem } from "../form";
import { Input } from "../input";
import { cn } from "../lib/utils";
import { useToast } from "../use-toast";

export default function ResetPasswordFrom() {
  const form = useForm({
    resolver: zodResolver(ResetPasswordFormSchema),
  });
  const { toast } = useToast();
  const router = useRouter();
  const searchParams = useSearchParams();
  const uid = searchParams.get("uid");
  const otp = searchParams.get("otp");
  const verification_type = searchParams.get("verification_type");

  const reset = async (
    code: string,
    email: string,
    verification_type: string,
    password: string,
  ) => {
    const response = await resetPassword({
      code,
      otp_type: base64ToString(verification_type),
      email: base64ToString(email),
      password,
    });

    if (response.message && response.status === 200) {
      router.push("/signin");
    }

    toast({
      className: cn(
        "top-0 right-0 flex fixed md:max-w-[420px] md:top-4 md:right-4 text-red-500",
      ),
      title: "Failed to update password",
      description: response.message,
    });
  };

  const onSubmit = (data: any) => {
    console.log(data);
    const currentData = data as {
      new_password: string;
      confirm_password: string;
    };
    reset(
      otp as string,
      uid as string,
      verification_type as string,
      currentData.new_password,
    ).catch((error) => console.log(error));
  };

  return (
    <Form {...form}>
      <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4 mb-4">
        <FormField
          control={form.control}
          name="new_password"
          render={({ field }) => (
            <FormItem>
              <FormControl>
                <Input type="password" {...field} placeholder="********" />
              </FormControl>
            </FormItem>
          )}
        />
        <FormField
          control={form.control}
          name="confirm_password"
          render={({ field }) => (
            <FormItem>
              <FormControl>
                <Input type="password" {...field} placeholder="********" />
              </FormControl>
            </FormItem>
          )}
        />
        <div className="space-y-6">
          <Button
            onClick={onSubmit}
            type="submit"
            className="w-full flex items-center mb-6"
          >
            Submit
          </Button>
        </div>
        <p className="mt-10 text-center text-sm text-gray-500">
          Want to sign in to your account?{" "}
          <Link
            href="/signin"
            className="font-semibold leading-6 text-secondary-foreground"
          >
            Log in
          </Link>
        </p>
      </form>
    </Form>
  );
}
