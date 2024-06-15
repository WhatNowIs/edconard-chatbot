import Image from "next/image";
import { Button } from "./ui/button";

const Harmurger = () => (
    <svg className="w-6 h-6 cursor-pointer" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16"></path>
    </svg>
)

const EdConardLogo = () => (    
    <svg version="1.0" width="35" height="35" viewBox="0 0 512.000000 512.000000"
    preserveAspectRatio="xMidYMid meet">
        <g transform="translate(0.000000,512.000000) scale(0.100000,-0.100000)"
        fill="#000000" stroke="none">
        <path d="M2332 5110 c-208 -20 -465 -78 -648 -145 -55 -20 -166 -69 -249 -110
        -280 -137 -450 -259 -680 -490 -231 -230 -353 -400 -490 -680 -89 -181 -135
        -304 -180 -479 -130 -511 -108 -1021 67 -1512 53 -150 177 -399 265 -534 431
        -656 1135 -1079 1917 -1151 156 -14 446 -7 596 16 549 82 1048 333 1440 725
        334 335 562 738 674 1190 49 200 66 324 73 536 7 216 -6 381 -48 587 -99 496
        -337 941 -693 1299 -206 207 -414 356 -677 487 -250 125 -491 201 -764 242
        -150 23 -461 32 -603 19z m1390 -1370 c377 -36 628 -201 749 -492 35 -86 74
        -238 84 -332 l7 -66 -294 0 -294 0 -14 67 c-17 89 -80 211 -131 258 -86 77
        -230 115 -360 94 -291 -47 -458 -383 -420 -844 20 -234 75 -381 177 -475 115
        -105 322 -136 513 -78 51 16 75 31 116 72 59 58 86 125 106 257 l12 79 295 0
        295 0 -7 -61 c-31 -270 -180 -529 -386 -669 -246 -167 -599 -221 -915 -140
        -102 26 -261 103 -348 170 -296 225 -450 562 -449 985 2 791 493 1248 1264
        1175z m-1442 -275 l0 -235 -572 -2 -573 -3 -3 -197 -2 -198 495 0 495 0 0
        -235 0 -235 -492 -2 -493 -3 0 -230 0 -230 583 -3 582 -2 0 -235 0 -235 -870
        0 -870 0 0 1140 0 1140 860 0 860 0 0 -235z"/>
        </g>
    </svg>
)

const PlusIcon = () => (
    <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"></path>
    </svg>
)

const ShevronDown = () => (
    <svg className="w-5 h-5 text-gray-500 cursor-pointer" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 9l6 6 6-6"></path>
    </svg>
)

const ShevronUp = () => (
    <svg className="w-5 h-5 text-gray-500 cursor-pointer" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M18 15l-6-6-6 6"></path>
    </svg>

)

export default function LeftNav() {
  return (
    <div className="w-64 flex flex-col h-screen bg-white border-r border-gray-200 p-4">
        <div className="w-full flex mb-4 justify-between items-center gap-2">
            <div className="flex gap-2">
                <EdConardLogo />
                <span className="text-2xl">CRI</span>
            </div>
            <Harmurger />
        </div>
        <div className="flex items-center mb-6 border p-2 rounded-md">
            <Image 
                src="https://via.placeholder.com/40" 
                alt="Profile Picture" 
                width={40}
                height={40} 
                className="w-10 h-10 rounded-full mr-3" 
            />
            <div>
            <div className="text-sm text-gray-500">Marc Hill</div>
            <div className="text-sm text-gray-500 text-xs">mhill@edconard.com</div>
            </div>
        </div>
        
        <Button type="submit" className="w-full flex items-center mb-6">
            <PlusIcon />
            New Thread
        </Button>
        <div className="mb-6">
            <div className="flex justify-between items-center text-gray-700 mb-2">
            <div className="font-semibold">Workspaces</div>
            <ShevronDown />
            </div>
            <div className="text-gray-600">Edward Conard's Co...</div>
        </div>
        <div className="mb-6">
            <div className="flex justify-between items-center text-gray-700 mb-2">
            <div className="font-semibold">Recent Threads</div>
                <ShevronDown />
            </div>
            <div className="text-gray-600 my-2 cursor-pointer">Capitalisms Class Debate</div>
            <div className="text-gray-600 my-2 cursor-pointer">Capitalisms Impact</div>
            <div className="text-gray-600 my-2 cursor-pointer">Capitalisms Effectiveness</div>
            <div className="text-gray-600 my-2 cursor-pointer">Untitled Thread</div>
        </div>
        <div className="mb-6">
            <div className="flex justify-between items-center text-gray-700 mb-2">
            <div className="font-semibold">Chat Bundles</div>
            <ShevronDown />
            </div>
        </div>
        <div>
            <div className="flex justify-between items-center text-gray-700 mb-2">
            <div className="font-semibold">Marketplace</div>
            <ShevronDown />
            </div>
            <div className="text-gray-600">Naval Ravikant</div>
        </div>
    </div>
  );
}
