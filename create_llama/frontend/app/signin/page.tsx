import SigninForm from "../components/ui/account/signin-form";
import { Google, Microsoft } from "../components/ui/chat/icons/main-icons";

export default function Signin() {
    return (
      <>
        <div className="flex min-h-full flex-1 flex-col justify-center py-12 sm:px-6 lg:px-8">
            <div className="items-center sm:mx-auto sm:w-full sm:max-w-md">
                <h2 className="mt-6 text-center text-2xl font-bold leading-9 tracking-tight text-gray-900">
                Sign in to your account
                </h2>
            </div>
  
          <div className="mt-10 sm:mx-auto sm:w-full sm:max-w-[480px]">
            <div className="bg-white px-6 py-12 shadow sm:rounded-lg sm:px-12">
                <SigninForm />
                <div>
                    <div className="relative mt-10">
                    <div className="absolute inset-0 flex items-center" aria-hidden="true">
                        <div className="w-full border-t border-gray-200" />
                    </div>
                    <div className="relative flex justify-center text-sm font-medium leading-6">
                        <span className="bg-white px-6 text-gray-900">Or continue with</span>
                    </div>
                    </div>
    
                    <div className="mt-6 grid grid-cols-2 gap-4">
                    <a
                        href="#"
                        className="flex w-full items-center justify-center gap-3 rounded-md bg-white px-3 py-2 text-sm font-semibold text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 hover:bg-gray-50 focus-visible:ring-transparent"
                    >
                        <Google />
                        <span className="text-sm font-semibold leading-6">Google</span>
                    </a>
    
                    <a
                        href="#"
                        className="flex w-full items-center justify-center gap-3 rounded-md bg-white px-3 py-2 text-sm font-semibold text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 hover:bg-gray-50 focus-visible:ring-transparent"
                    >
                        <Microsoft />
                        <span className="text-sm font-semibold leading-6">Microsoft</span>
                    </a>
                    </div>
                </div>
            </div>
            <p className="mt-10 text-center text-sm text-gray-500">
                Not a member?{' '}
                <a href="#" className="font-semibold leading-6 text-secondary-foreground">
                    Create a new account
                </a>
            </p>
          </div>
        </div>
      </>
    )
  }
  