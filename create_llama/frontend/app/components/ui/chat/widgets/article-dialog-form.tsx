"use client";

/* eslint-disable @typescript-eslint/no-explicit-any */
import ChatContext from "@/app/context/chat-context";
import {
  MacroRoundupSchema,
  MacroRoundupType,
  saveMacroRoundupData,
} from "@/app/service/user-service";
import { zodResolver } from "@hookform/resolvers/zod";
import { useContext, useState } from "react";
import { useForm } from "react-hook-form";
import { SubmitButton } from "../../custom/submitButton";
import { Form, FormControl, FormField, FormItem, FormLabel } from "../../form";
import { Input } from "../../input";
import { cn } from "../../lib/utils";
import { useToast } from "../../use-toast";

export interface Props {
  close: () => void;
}

export default function MacroRoundupForm(props: Props) {
  const chatContext = useContext(ChatContext);
  const form = useForm({
    resolver: zodResolver(MacroRoundupSchema),
  });
  const { toast } = useToast();
  const [isSubmitting, setIsSubmitting] = useState<boolean>(false);

  const onSubmit = async (data: any) => {
    setIsSubmitting(true);
    // Send the data to the server
    try {
      const response = await saveMacroRoundupData(data as MacroRoundupType);

      if (chatContext && !("message" in response)) {
        const { setArticle } = chatContext;

        setArticle(response);
        console.log(data);
        props.close();
      } else {
        throw Error(
          "An error has occurred while fetching and storing article data",
        );
      }
    } catch (err: any) {
      console.error(err);
      toast({
        className: cn(
          "top-0 right-0 flex fixed md:max-w-[420px] md:top-4 md:right-4 text-red-500",
        ),
        title: "Failed to update config",
        description: err?.message,
      });
    }
    setIsSubmitting(false);
  };

  return (
    <Form {...form}>
      <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4 mb-4">
        <div className="flex flex-col gap-4">
          <FormField
            control={form.control}
            name="document_link"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Link</FormLabel>
                <FormControl>
                  <Input
                    {...field}
                    type="url"
                    placeholder="Provide a link to the google doc url"
                  />
                </FormControl>
              </FormItem>
            )}
          />
          <FormField
            control={form.control}
            name="order"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Article by Order of Appearance</FormLabel>
                <FormControl>
                  <Input
                    {...field}
                    type="number"
                    className="w-2/4"
                    placeholder="Article #"
                  />
                </FormControl>
              </FormItem>
            )}
          />
        </div>
        <SubmitButton
          isSubmitting={isSubmitting}
          text="Start"
          className="w-full flex items-center"
        />
      </form>
    </Form>
  );
}
