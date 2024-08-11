import { getBackendURL } from "@/app/service/utils";
import { NextRequest, NextResponse } from "next/server";

export async function GET(req: NextRequest) {
  const authHeader = req.headers.get("authorization");

  // Check if the Authorization header is present and starts with "Bearer "
  if (!authHeader || !authHeader.startsWith("Bearer ")) {
    return NextResponse.json({ message: "Not authenticated" }, { status: 401 });
  }

  const token = authHeader.split(" ")[1];

  console.log("Token:", token);

  const response = await fetch(`${getBackendURL()}/api/chat/article`, {
    method: "GET",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
    },
  });

  if (!response.ok) {
    throw new Error("Session verification failed");
  }

  const article = await response.json();

  return NextResponse.json(article, { status: 200 });
}
