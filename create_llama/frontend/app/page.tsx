import ChatSection from "@/app/components/chat-section";
import LeftNav from "@/app/components/left-nav";
import RightNav from "@/app/components/right-nav";

export default function Home() {
  return (
      <main className="flex min-h-screen">
        <LeftNav />
        <ChatSection />
        <RightNav />
      </main>
  );
}
