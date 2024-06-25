import React from 'react'; 
import Link from "next/link";
import ForgotPasswordForm from "../components/ui/auth/forgot-password-form";

export default function ForgotPassword() {
    return (
      <>
        <div className="flex min-h-full flex-1 flex-col justify-center py-12 sm:px-6 lg:px-8">
            <div className="items-center sm:mx-auto sm:w-full sm:max-w-md">
                <h2 className="mt-6 text-center text-2xl font-bold leading-9 tracking-tight text-gray-900">
                Forgot password
                </h2>
            </div>
  
          <div className="mt-10 sm:mx-auto sm:w-full sm:max-w-[480px]">
            <div className="bg-white px-6 py-12 shadow sm:rounded-lg sm:px-12">
                <ForgotPasswordForm />
            </div>
            <p className="mt-10 text-center text-sm text-gray-500">
                Have an account already?{' '}
                <Link href="/signin" className="font-semibold leading-6 text-secondary-foreground">
                    Log in
                </Link>
            </p>
          </div>
        </div>
      </>
    )
  }
  