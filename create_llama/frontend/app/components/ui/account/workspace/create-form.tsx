"use client";

import {
  WorkspaceCreate,
  WorkspaceCreateSchema,
} from "@/app/service/workspace-service";
import { zodResolver } from "@hookform/resolvers/zod";
import { useForm } from "react-hook-form";
import { SubmitButton } from "../../custom/submitButton";
import { Form, FormControl, FormField, FormItem, FormLabel } from "../../form";
import { Input } from "../../input";
import { cn } from "../../lib/utils";
import { Toaster } from "../../toaster";
import { useToast } from "../../use-toast";

interface WorkspaceCreationFormProps {
  handleCreateWorkspace: (data: WorkspaceCreate) => Promise<void>;
}

export const WorkspaceCreationForm = ({
  handleCreateWorkspace,
}: WorkspaceCreationFormProps) => {
  const { toast } = useToast();
  const form = useForm<WorkspaceCreate>({
    resolver: zodResolver(WorkspaceCreateSchema),
  });

  const onSubmit = async (data: WorkspaceCreate) => {
    try {
      await handleCreateWorkspace(data);
      toast({
        className: cn(
          "top-0 right-0 flex fixed md:max-w-[420px] md:top-4 md:right-4 text-green-500",
        ),
        title: "Workspace created.",
        description: `${data.name} workspace has successfully been created.`,
      });
      form.setValue("name", "");
    } catch (error) {
      toast({
        className: cn(
          "top-0 right-0 flex fixed md:max-w-[420px] md:top-4 md:right-4 text-red-500",
        ),
        title: "Failed to create workspace.ss",
      });
    }
  };

  return (
    <Form {...form}>
      <form
        onSubmit={form.handleSubmit(onSubmit)}
        className="w-full space-y-4 mb-4 grid grid-cols-1 gap-x-6 gap-y-3 sm:max-w-xl sm:grid-cols-3"
      >
        <FormField
          control={form.control}
          name="name"
          render={({ field }) => (
            <FormItem className="sm:col-span-3">
              <FormLabel>Workspace Name</FormLabel>
              <FormControl>
                <Input type="text" {...field} />
              </FormControl>
            </FormItem>
          )}
        />
        <SubmitButton
          isSubmitting={form.formState.isSubmitting}
          text="Create Workspace"
          className="flex items-center"
        />
      </form>
      <Toaster />
    </Form>
  );
};

export default WorkspaceCreationForm;
