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

  const token = authHeader.split(" ")[1];

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
        
      Here are all the predefined topics and subtopics, do not return anything which is not listed here:     
      "1. Comparisons:
          - Age
          - Cross-country
          - Gender
          - Geography (Urban/Rural)
          - Historical
          - Liberal/Conservative
          - No Comparison
          - Other Comparison
          - Race
          - Sector
          - Skill Level
      
      2. Fiscal Policy:
          - Fiscal Deficits
          - Government Spending
          - Infrastructure
          - Multiplier/Rational Expectations
          - Regulation
          - Taxation
      
      3. GDP:
          - Business Cycle
          - Financial Markets
          - Growth
          - Housing
          - Inflation
          - Savings Glut/Trade Deficit
          - Trade (not deficits)
      
      4. Monetary Policy:
          - Banking
          - Financial Crisis
          - M&M
      
      5. Science:
          - Cosmos
          - Evolution/Heredity
          - Fraudulent Studies
          - Global Warming
          - Other Science
      
      6. Workforce:
          - Demographics
          - Education
          - Family/Marriage
          - Gender Pay Gap
          - Immigration
          - Inequality
          - Minimum Wage
          - Mobility/Assortive Mating
          - Poverty/Crime
          - Unemployment/Participation
          - Wages/Income
          - Workforce Reorganization/Participation
      
      7. Productivity:
          - Cronyism
          - Incentives/Risk-Taking
          - Innovation/Research
          - Institutional Capabilities
          - Intangibles
          - Investment
          - Startups
          - Workforce Reorganization/Participation
      
      8. Energy"
      Question: ${input}
    `,
    },
  ];

  const response = await fetch("http://54.89.10.40/chat/stream", {
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
