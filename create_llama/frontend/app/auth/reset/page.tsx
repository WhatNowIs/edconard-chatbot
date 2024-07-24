import React from 'react'; 
import ResetPasswordFrom from "@/app/components/ui/auth/reset-password";
import { Suspense } from "react";

export default function VerifyAccount() {
    return (
      <>
        <div className="flex min-h-full flex-1 flex-col justify-center py-12 sm:px-6 lg:px-8">
            <div className="items-center sm:mx-auto sm:w-full sm:max-w-md">
                <h2 className="mt-6 text-center text-2xl font-bold leading-9 tracking-tight text-gray-900">
                Reset password
                </h2>
            </div>
  
          <div className="mt-10 sm:mx-auto sm:w-full sm:max-w-[480px]">
            <div className="bg-white px-6 py-12 shadow sm:rounded-lg sm:px-12">
              <Suspense fallback={<div>Loading...</div>}>
                <ResetPasswordFrom />
              </Suspense>
            </div>
          </div>
        </div>
      </>
    )
  }
  