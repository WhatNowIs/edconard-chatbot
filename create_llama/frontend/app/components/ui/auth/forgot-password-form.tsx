"use client"

import { Button } from "../button";
import { useRouter } from 'next/navigation';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { ForgotPasswordSchema, ForgotPasswordType, forgotPassword } from '@/app/service/user-service';
import { Form, FormControl, FormField, FormItem } from "../form";
import { Input } from "../input";

export default function ForgotPasswordForm(){
    const form = useForm({
        resolver: zodResolver(ForgotPasswordSchema),
    })
    const router = useRouter();

    const forgot = async (data: any) => {
        const response = await forgotPassword(data as ForgotPasswordType);        
        if(response.message){
            router.push("/auth/reset-password-msg");
        }
    }
    
    const onSubmit = (data: any) => {
       forgot(data).catch((error) => console.log(error))
    }

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
                    <Button onClick={onSubmit} type="submit" className="w-full flex items-center mb-6">
                        Submit
                    </Button>
                </div>
            </form>
        </Form>
    )
}