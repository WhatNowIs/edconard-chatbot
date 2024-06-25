"use client"
/* eslint-disable @typescript-eslint/no-explicit-any */
import React from 'react'; 
import { useEffect, useState } from "react";
import { useSearchParams } from 'next/navigation';
import { Button } from "../button";
import { useRouter } from 'next/navigation';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { VerifyAccountSchema, VerifyOtpType, verifyOtp, resendActivationOtp } from '@/app/service/user-service';
import { Form, FormControl, FormField, FormItem } from "../form";
import { Input } from "../input";
import { cn } from "../lib/utils";
import { useToast } from "../use-toast";
import base64ToString from "@/app/utils/shared";

export default function VerifyAccountForm(){
    const form = useForm({
        resolver: zodResolver(VerifyAccountSchema),
    });
    const { toast } = useToast();
    const router = useRouter();
    const searchParams = useSearchParams();
    const uid = searchParams.get('uid');
    const otp = searchParams.get('otp');
    const verification_type = searchParams.get('verification_type');
    const [hasVerified, setHasVerified] = useState<boolean>(false);

    const verify = async (code: string, email: string, verification_type: string) => {
        const response = await verifyOtp({
            code,
            otp_type: base64ToString(verification_type),
            email: base64ToString(email)
        });

        alert(response.message);

        if(response.status === 400){
            toast({
                className: cn(
                "top-0 right-0 flex fixed md:max-w-[420px] md:top-4 md:right-4 text-red-500",
                ),
                title: response.message,
            });    
            router.push("/signin");
        }
        else{
            toast({
                className: cn(
                "top-0 right-0 flex fixed md:max-w-[420px] md:top-4 md:right-4 text-green-500",
                ),
                title: response.message,
            });
            router.push("/");
        }
    }

    useEffect(() => {
        if(uid && otp && verification_type && !hasVerified){
            setHasVerified(true);
            verify(otp, uid, verification_type).catch((error: any) => console.log(error));            
        }
    }, [uid, otp, verification_type]);

    const onSubmit = (data: any) => {
        const currentData = data as VerifyOtpType;
        
        verify( currentData.code, uid as string, verification_type as string).catch((error) => console.log(error));
    }

    const resendOtp = (email: string) => {
        resendActivationOtp(email).catch((error) => console.log(error));
    }
    

    return (   
        <Form {...form}>
            <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4 mb-4">     
                <FormField
                    control={form.control}
                    name="code"
                    render={({ field }) => (
                    <FormItem>
                        <FormControl>
                        <Input type="number" {...field} placeholder="Otp" />
                        </FormControl>
                    </FormItem>
                    )}
                />
                <div className="flex gap-2 text-sm leading-6">
                    <span>Didn&apos;t recieve code? </span>
                    <button onClick={() => resendOtp(base64ToString(uid as string))} className="border-none bg-white font-semibold text-secondary-foreground">
                        resend
                    </button>
                </div>
                <div className="space-y-6">
                    <Button onClick={onSubmit} type="submit" className="w-full flex items-center mb-6">
                        Submit
                    </Button>
                </div>
            </form>
        </Form>
    )
}