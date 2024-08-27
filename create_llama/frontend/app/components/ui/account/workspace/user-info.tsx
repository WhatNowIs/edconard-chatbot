"use client";
import { UserFormType } from "@/app/service/user-service"; // Adjust the path as necessary
import { EntityStatus, UserRole } from "@/app/utils/multi-mode-select";
import { zodResolver } from "@hookform/resolvers/zod";
import { useEffect, useState } from "react";
import { useForm } from "react-hook-form";
import { z } from "zod";
import { SubmitButton } from "../../custom/submitButton";
import { Form, FormControl, FormField, FormItem, FormLabel } from "../../form";
import { Input } from "../../input";
import {
  Select,
  SelectContent,
  SelectGroup,
  SelectItem,
  SelectLabel,
  SelectTrigger,
  SelectValue,
} from "../../select";
import { Toaster } from "../../toaster";
import { useToast } from "../../use-toast";

// Rag config scheme
export const UserInfoSchema = z.object({
  first_name: z.string(),
  last_name: z.string(),
  email: z.string(),
  phone_number: z.string(),
  role: z.string(),
  status: z.string(),
});

export type UserInfo = z.TypeOf<typeof UserInfoSchema>;

export default function UserInfoForm({ user }: { user: UserFormType | null }) {
  const form = useForm<UserInfo>({
    resolver: zodResolver(UserInfoSchema),
  });
  const { toast } = useToast();
  const [isSubmitting, setIsSubmitting] = useState<boolean>(false);

  const onSubmit = async (data: any) => {
    setIsSubmitting(true);
    try {
      // Handle form submission logic here
      console.log("Form data:", data);
      // Example: Simulate successful submission
      toast({
        title: "Form submitted successfully",
        description: "User data has been saved.",
      });
    } catch (err) {
      console.error(err);
      toast({
        title: "Failed to submit the form",
        description: "An error occurred.",
        className: "text-red-500",
      });
    }
    setIsSubmitting(false);
  };

  useEffect(() => {
    if (user && user !== null) {
      form.setValue("first_name", user.first_name);
      form.setValue("last_name", user.last_name);
      form.setValue("email", user.email);
      form.setValue("role", user.role?.name as string);
      form.setValue("phone_number", user.phone_number);
      form.setValue("status", user.status as string);
    }
  }, [user]);

  const handleSubmitRole = async (value: string) => {
    console.log("Updated", value);
  };

  const handleSubmitStatus = async (value: string) => {
    console.log("Updated", value);
  };

  return (
    <>
      <Form {...form}>
        <form
          onSubmit={form.handleSubmit(onSubmit)}
          className="w-full space-y-4 mb-4 overflow-y-auto px-2"
        >
          <FormField
            control={form.control}
            name="first_name"
            render={({ field }) => (
              <FormItem>
                <FormLabel>First Name</FormLabel>
                <FormControl>
                  <Input {...field} disabled />
                </FormControl>
              </FormItem>
            )}
          />
          <FormField
            control={form.control}
            name="last_name"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Last Name</FormLabel>
                <FormControl>
                  <Input {...field} disabled />
                </FormControl>
              </FormItem>
            )}
          />
          <FormField
            control={form.control}
            name="email"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Email</FormLabel>
                <FormControl>
                  <Input type="email" {...field} disabled />
                </FormControl>
              </FormItem>
            )}
          />
          <FormField
            control={form.control}
            name="phone_number"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Phone Number</FormLabel>
                <FormControl>
                  <Input {...field} disabled />
                </FormControl>
              </FormItem>
            )}
          />

          <FormField
            control={form.control}
            name="role"
            render={({ field }) => (
              <FormItem>
                <form
                  onSubmit={() => handleSubmitRole(field.value)}
                  className="flex items-center space-x-2"
                >
                  <FormControl>
                    <Select
                      onValueChange={(value) => form.setValue("role", value)}
                      value={field.value}
                    >
                      <SelectTrigger>
                        <SelectValue placeholder="Choose a role" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectGroup>
                          <SelectLabel>Roles</SelectLabel>
                          {Object.values(UserRole).map((role) => (
                            <SelectItem key={role} value={role}>
                              {role}
                            </SelectItem>
                          ))}
                        </SelectGroup>
                      </SelectContent>
                    </Select>
                  </FormControl>
                  <SubmitButton
                    isSubmitting={isSubmitting}
                    text="Update"
                    className="flex items-center"
                  />
                </form>
              </FormItem>
            )}
          />

          <FormField
            control={form.control}
            name="status"
            render={({ field }) => (
              <FormItem>
                <form
                  onSubmit={() => handleSubmitStatus(field.value)}
                  className="flex items-center space-x-2"
                >
                  <FormControl>
                    <Select
                      onValueChange={(value) => form.setValue("status", value)}
                      value={field.value}
                    >
                      <SelectTrigger>
                        <SelectValue placeholder="Account status" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectGroup>
                          <SelectLabel>Status</SelectLabel>
                          {Object.values(EntityStatus).map((role) => (
                            <SelectItem key={role} value={role}>
                              {role}
                            </SelectItem>
                          ))}
                        </SelectGroup>
                      </SelectContent>
                    </Select>
                  </FormControl>
                  <SubmitButton
                    isSubmitting={isSubmitting}
                    text="Update"
                    className="flex items-center"
                  />
                </form>
              </FormItem>
            )}
          />
          <Toaster />
        </form>
      </Form>
    </>
  );
}
