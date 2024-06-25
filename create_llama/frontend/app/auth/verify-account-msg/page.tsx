import React from 'react'; 
import Link from "next/link";

export default function VerifyMessage() {
    return (
      <>
        <div className="flex min-h-full flex-1 flex-col justify-center items-center h-screen py-12 sm:px-6 lg:px-8">
            <div className="items-center sm:mx-auto mx-w-full sm:w-full sm:max-w-md my-4">
                <p>An email with a verification link has been sent your email address, please follow the link to activate your account.</p>
            </div>       
            <p className="mt-10 text-center text-sm text-gray-500">
                Go back to ?{' '}
                <Link href="/signin" className="font-semibold leading-6 text-secondary-foreground">
                    Login
                </Link>
            </p>
        </div>
      </>
    )
  }
  