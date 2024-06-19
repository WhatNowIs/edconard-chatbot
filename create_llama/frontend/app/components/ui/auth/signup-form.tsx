"use client"

import { useEffect, useState } from "react";
import { useRouter } from 'next/navigation';
import { UserFormType, UserSchema, createUserAccount } from "@/app/service/user-service";
import { useForm } from 'react-hook-form';
import { Form, FormControl, FormField, FormItem, FormLabel } from "../form";
import { zodResolver } from "@hookform/resolvers/zod";
import { Input } from "../input";
import { useToast } from "../use-toast";
import { cn } from "../lib/utils";
import { SubmitButton } from "../custom/submitButton";

export default function SignupForm(){
    const form = useForm({
        resolver: zodResolver(UserSchema),
    })
    const { toast } = useToast();
    const router = useRouter();
    const [isSubmitting, setIsSubmitting] = useState<boolean>(false);

    const onSubmit = async (data: any) => {        
        setIsSubmitting(true);
        // Send the data to the server
        try {
            const configData = await createUserAccount(data as UserFormType);
            console.log(configData);

            router.push("/signin");
        } catch (err) {
            console.error(err);
            toast({
                className: cn(
                "top-0 right-0 flex fixed md:max-w-[420px] md:top-4 md:right-4 text-red-500",
                ),
                title: "Failed to update config",
            });
        }
        setIsSubmitting(false);
    }

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
                <SubmitButton isSubmitting={isSubmitting} text="Create" className="w-full flex items-center" />           
            </form>
        </Form>
    )
}