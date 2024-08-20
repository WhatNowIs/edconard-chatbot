import { getMacroRoundupData } from "@/app/service/user-service";
import { Article } from "@/app/utils/multi-mode-select";
import { NextRequest, NextResponse } from "next/server";

export async function POST(req: NextRequest) {
  const { data, input } = await req.json();

  const authHeader = req.headers.get("authorization");

  // Check if the Authorization header is present and starts with "Bearer "
  if (!authHeader || !authHeader.startsWith("Bearer ")) {
    return NextResponse.json({ message: "Not authenticated" }, { status: 401 });
  }

  const articleData: Article = (await getMacroRoundupData()) as Article;

  const article_data = `
    Headline="${articleData.headline}"
    Authors="${articleData.authors}"
    Summary="${articleData.abstract}"
    Publisher="${articleData.publisher}"
  `;

  const cleanedData: { role: string; content: string }[] = data.map(
    (c: { role: string; content: string }) => {
      return { role: c.role, content: c.content };
    },
  );

  const messagesData = [
    ...cleanedData,
    {
      role: "user",
      content: `
      Here is the article data: ${article_data}\n
      Question: ${input}

      N.B: - Never return duplicates in your answer.
           - Always tell the user the fields you are using to guide your generation.
    `,
    },
  ];

  const response = await fetch("http://54.234.177.154/chat/stream", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Accept: "text/event-stream",
    },
    body: JSON.stringify(messagesData),
  });

  if (!response.ok) {
    return NextResponse.json(
      { error: "Failed to connect to stream" },
      { status: 500 },
    );
  }

  const reader =
    response.body?.getReader() as ReadableStreamDefaultReader<Uint8Array>;
  const decoder = new TextDecoder("utf-8");

  return new NextResponse(
    new ReadableStream({
      async start(controller) {
        while (true) {
          const { value, done } = await reader.read();
          if (done) {
            break;
          }
          const chunk = decoder.decode(value);
          controller.enqueue(chunk);
        }
        controller.close();
      },
      cancel() {
        reader.releaseLock();
      },
    }),
    {
      headers: {
        "Content-Type": "text/event-stream",
        "Cache-Control": "no-cache",
      },
    },
  );
}
