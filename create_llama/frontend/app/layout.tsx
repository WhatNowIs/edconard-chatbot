import type { Metadata } from "next";
import { Inter } from "next/font/google";
import React from "react";
import { AuthProvider } from "./context/auth-context";
import { ChatProvider } from "./context/chat-context";
import "./globals.css";
import "./markdown.css";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "Coherent Research Institute",
  description: `
    AI-powered chatbot designed to answer questions and deliver insights regarding macroeconomics. 
    The chatbot will mimic the rhetorical and analytical style of Edward Conard,
  `,
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <AuthProvider>
          <ChatProvider>{children}</ChatProvider>
        </AuthProvider>
      </body>
    </html>
  );
}
