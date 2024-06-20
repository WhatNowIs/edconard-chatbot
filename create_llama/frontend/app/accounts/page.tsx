import LeftNav from "@/app/components/left-nav";
import RightNav from "@/app/components/right-nav";
import { Button } from "@/app/components/ui/button";
import { Input } from "@/app/components/ui/input";
import UpdateProfile from "@/app/components/ui/account/update-profile";
import AccountOverview from "@/app/components/ui/account/account-overview"


export default function AccountSettings() {    

    return (
        <div className="w-full flex h-screen">
                <LeftNav />
                <main className="w-full h-screen items-center flex flex-col overflow-auto">
                    <div className="grid w-full grid-cols-1 gap-y-10 px-4 py-16 sm:px-6 md:grid-cols-3 lg:px-8 py-6">
                        <UpdateProfile />
                        <AccountOverview />
                    </div>

                    <div className="grid w-full grid-cols-1 gap-y-10 px-4 py-16 sm:px-6 md:grid-cols-3 lg:px-8">
                        <div>
                            <h2 className="text-base font-semibold leading-7 ">Change password</h2>
                            <p className="mt-1 text-sm leading-6 text-gray-400">
                                Update your password associated with your account.
                            </p>
                        </div>

                        <form className="md:col-span-2">
                            <div className="grid grid-cols-1 gap-x-6 gap-y-4 sm:max-w-xl sm:grid-cols-6">
                                <div className="col-span-full">
                                    <label htmlFor="current-password" className="block text-sm font-medium leading-6 ">
                                        Current password
                                    </label>
                                    <div className="mt-2">                     
                                        <Input
                                            autoFocus
                                            name="message"
                                            placeholder="Current message"
                                            className="flex-1"
                                        />
                                    </div>
                                </div>

                                <div className="col-span-full">
                                    <label htmlFor="new-password" className="block text-sm font-medium leading-6 ">
                                        New password
                                    </label>
                                    <div className="mt-2">                     
                                        <Input
                                            autoFocus
                                            name="message"
                                            placeholder="New password"
                                            className="flex-1"
                                        />
                                    </div>
                                </div>

                                <div className="col-span-full">
                                    <label htmlFor="confirm-password" className="block text-sm font-medium leading-6 ">
                                        Confirm password
                                    </label>
                                    <div className="mt-2">                     
                                        <Input
                                            autoFocus
                                            name="message"
                                            placeholder="Confirm password"
                                            className="flex-1"
                                        />
                                    </div>
                                </div>
                            </div>
                            <div className="mt-8 flex">
                                <Button >
                                    Save
                                </Button>
                            </div>
                        </form>
                    </div>

                    <div className="grid w-full grid-cols-1 gap-y-10 gap-x-4 px-4 py-16 sm:px-6 md:grid-cols-3 lg:px-8">
                        <div>
                            <h2 className="text-base font-semibold leading-7 ">Log out other sessions</h2>
                            <p className="mt-1 text-sm leading-6 text-gray-400">
                                Please enter your password to confirm you would like to log out of your other sessions across all of
                                your devices.
                            </p>
                        </div>

                        <form className="md:col-span-2">
                            <div className="grid grid-cols-1 gap-x-6 gap-y-8 sm:max-w-xl sm:grid-cols-6">
                                <div className="col-span-full">
                                <label htmlFor="logout-password" className="block text-sm font-medium leading-6 ">
                                    Your password
                                </label>
                                <div className="mt-2">                     
                                    <Input
                                        autoFocus
                                        name="message"
                                        placeholder="Your password"
                                        className="flex-1"
                                    />
                                </div>
                                </div>
                            </div>

                            <div className="mt-8 flex">
                                <Button>
                                    Log out other sessions
                                </Button>
                            </div>
                        </form>
                    </div>

                    <div className="grid w-full grid-cols-1 gap-y-10 px-4 py-16 sm:px-6 md:grid-cols-3 lg:px-8">
                        <div>
                            <h2 className="text-base font-semibold leading-7 ">Delete account</h2>
                            <p className="mt-1 text-sm leading-6 text-gray-400">
                                No longer want to use our service? You can delete your account here. This action is not reversible.
                                All information related to this account will be deleted permanently.
                            </p>
                        </div>

                        <form className="flex items-start md:col-span-2">                    
                            <button
                                type="submit"
                                className="rounded-md bg-red-500 px-3 py-2 mt-1 text-sm font-semibold text-white shadow-sm hover:bg-red-400"
                            >
                                Yes, delete my account
                            </button>
                        </form>
                    </div>
                </main>
            <RightNav />
        </div>
    )
}
