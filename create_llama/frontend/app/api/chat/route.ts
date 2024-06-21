import { NextResponse, NextRequest } from 'next/server';

export async function GET(req: NextRequest) {
  const token = req.cookies.get('access_token');
  const OPENAI_API_KEY = process.env.OPENAI_API_KEY;

  if (!token) {
    console.error('No access token provided');
    return NextResponse.json({ message: 'Not authenticated' }, { status: 401 });
  }

  try {
    const question = req.nextUrl.searchParams.get('question');
    if (!question) {
      console.error('No question provided');
      return NextResponse.json({ message: 'No question provided' }, { status: 400 });
    }

    const aiResponse = await fetch('https://api.openai.com/v1/chat/completions', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${OPENAI_API_KEY}`,
      },
      body: JSON.stringify({
        model: 'gpt-4',
        messages: [
          { role: 'system', content: 'You are a helpful assistant.' },
          { role: 'user', content: `Generate a title of less than 100 characters for a new thread based on the following question: ${question}` }
        ],
        max_tokens: 20,
        temperature: 0.7,
        stream: false,
      }),
    });

    if (!aiResponse.ok) {
      const errorText = await aiResponse.text();
      console.error('AI response error:', aiResponse.status, errorText);
      throw new Error(`Failed to fetch AI response: ${aiResponse.status} ${errorText}`);
    }

    const jsonResponse = await aiResponse.json();

    const title = jsonResponse.choices[0]?.message?.content.trim();

    if (!title) {
      throw new Error('Generated title is empty');
    }

    return NextResponse.json({ title }, { status: 200 });
  } catch (error) {
    console.error('Server error:', error);
    return NextResponse.json({ message: 'Internal Server Error' }, { status: 500 });
  }
}
