import Link from "next/link";
import ForgotPasswordForm from "../components/ui/auth/forgot-password-form";

export default function ResetPassword() {
    return (
      <>
        <div className="flex min-h-full flex-1 flex-col justify-center py-12 sm:px-6 lg:px-8">
            <div className="items-center sm:mx-auto sm:w-full sm:max-w-md">
                <h2 className="mt-6 text-center text-2xl font-bold leading-9 tracking-tight text-gray-900">
                Reset Password
                </h2>
            </div>
        </div>
      </>
    )
  }
  