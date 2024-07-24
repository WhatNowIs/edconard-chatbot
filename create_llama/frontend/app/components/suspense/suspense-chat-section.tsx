
import React from 'react';

export function SkeletonLeftNav() {
    return (
        <div className="w-80 flex flex-col h-screen bg-white border-r border-gray-200 p-4">
            <div className="w-full h-10 bg-gradient-to-r from-gray-50 via-gray-100 to-gray-50 bg-animate rounded mb-4"></div>
            <div className="flex items-center mb-6 border p-2 rounded-md">
                <div className="w-10 h-10 bg-gradient-to-r from-gray-50 via-gray-100 to-gray-50 bg-animate rounded-full mr-3"></div>
                <div>
                <div className="w-24 h-4 bg-gradient-to-r from-gray-50 via-gray-100 to-gray-50 bg-animate rounded mb-2"></div>
                <div className="w-32 h-4 bg-gradient-to-r from-gray-50 via-gray-100 to-gray-50 bg-animate rounded"></div>
                </div>
            </div>
            <div className="flex flex-col space-y-4">
                <div className="w-full h-10 bg-gradient-to-r from-gray-50 via-gray-100 to-gray-50 bg-animate rounded"></div>
                <div className="w-full h-10 bg-gradient-to-r from-gray-50 via-gray-100 to-gray-50 bg-animate rounded"></div>
                <div className="w-full h-10 bg-gradient-to-r from-gray-50 via-gray-100 to-gray-50 bg-animate rounded"></div>
                <div className="w-full h-10 bg-gradient-to-r from-gray-50 via-gray-100 to-gray-50 bg-animate rounded"></div>
            </div>
        </div>
    );
}

export default function SkeletonRightNav() {
    return (
        <div className="flex flex-col justify-between items-center w-14 h-screen bg-white border-l border-gray-200 p-4 animate-pulse">
        <div className="flex flex-col space-y-4">
            <div className="w-full h-5 bg-gradient-to-r from-gray-50 via-gray-100 to-gray-50 bg-animate rounded-lg mb-4"></div>
            <div className="w-full h-5 bg-gradient-to-r from-gray-50 via-gray-100 to-gray-50 bg-animate rounded-lg mb-4"></div>
            <div className="w-full h-5 bg-gradient-to-r from-gray-50 via-gray-100 to-gray-50 bg-animate rounded-lg"></div>
        </div>
        <div className="w-6 h-6 bg-gray-100 rounded-full"></div>
        </div>
    );
}

export function SkeletonChatSection() {
    return (
        <div className="flex flex-col space-y-4 justify-between w-full p-4 animate-pulse">
            <div className='w-[35%] h-10 flex gap-2 justify-center bg-gradient-to-r from-gray-50 via-gray-100 to-gray-50 bg-animate rounded'></div>
            <div className="w-full h-[80%] bg-gradient-to-r from-gray-50 via-gray-100 to-gray-50 bg-animate rounded"></div>
            <div className="w-full h-16 bg-gradient-to-r from-gray-50 via-gray-100 to-gray-50 bg-animate rounded"></div>
        </div>
    );
}

export function SuspenseMainChat(){
    return (
        <>
            <SkeletonLeftNav />
            <SkeletonChatSection />
            <SkeletonRightNav />
        </>
    )
}
