"use client";

import {
  ThreadManagementSchema,
  ThreadManagementType,
} from "@/app/service/workspace-service";
import { zodResolver } from "@hookform/resolvers/zod";
import { useForm } from "react-hook-form";
import { SubmitButton } from "../../custom/submitButton";
import { Form, FormControl, FormField, FormItem, FormLabel } from "../../form";
import { Input } from "../../input";
import { cn } from "../../lib/utils";
import { useToast } from "../../use-toast";

interface ThreadManagementFormProps {
  handleAddThread: (data: ThreadManagementType) => Promise<void>;
  handleRemoveThread: (data: ThreadManagementType) => Promise<void>;
}

export const ThreadManagementForm = ({
  handleAddThread,
  handleRemoveThread,
}: ThreadManagementFormProps) => {
  const { toast } = useToast();
  const form = useForm<ThreadManagementType>({
    resolver: zodResolver(ThreadManagementSchema),
  });

  const onSubmitAdd = async (data: ThreadManagementType) => {
    try {
      await handleAddThread(data);
      toast({
        className: cn(
          "top-0 right-0 flex fixed md:max-w-[420px] md:top-4 md:right-4 text-green-500",
        ),
        title: "Thread added successfully",
      });
    } catch (error) {
      toast({
        className: cn(
          "top-0 right-0 flex fixed md:max-w-[420px] md:top-4 md:right-4 text-red-500",
        ),
        title: "Failed to add thread",
      });
    }
  };

  const onSubmitRemove = async (data: ThreadManagementType) => {
    try {
      await handleRemoveThread(data);
      toast({
        className: cn(
          "top-0 right-0 flex fixed md:max-w-[420px] md:top-4 md:right-4 text-green-500",
        ),
        title: "Thread removed successfully",
      });
    } catch (error) {
      toast({
        className: cn(
          "top-0 right-0 flex fixed md:max-w-[420px] md:top-4 md:right-4 text-red-500",
        ),
        title: "Failed to remove thread",
      });
    }
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
              <FormLabel>Workspace ID</FormLabel>
              <FormControl>
                <Input type="text" {...field} />
              </FormControl>
            </FormItem>
          )}
        />
        <FormField
          control={form.control}
          name="thread_id"
          render={({ field }) => (
            <FormItem className="sm:col-span-3">
              <FormLabel>Thread ID</FormLabel>
              <FormControl>
                <Input type="text" {...field} />
              </FormControl>
            </FormItem>
          )}
        />
        <SubmitButton
          isSubmitting={form.formState.isSubmitting}
          text="Add Thread"
          className="flex items-center"
        />
      </form>
      <form
        onSubmit={form.handleSubmit(onSubmitRemove)}
        className="w-full space-y-4 mb-4 grid grid-cols-1 gap-x-6 gap-y-3 sm:max-w-xl sm:grid-cols-3"
      >
        <SubmitButton
          isSubmitting={form.formState.isSubmitting}
          text="Remove Thread"
          className="flex items-center"
        />
      </form>
    </Form>
  );
};

export default ThreadManagementForm;
