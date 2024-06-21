import { getBackendURL } from '@/app/service/utils';
import { NextResponse, NextRequest } from 'next/server';

export async function GET(req: NextRequest) {
  const token = req.cookies.get('access_token');

  if (!token) {
    return NextResponse.json({ message: 'Not authenticated' }, { status: 401 });
  }

  try {
    const response = await fetch(`${getBackendURL()}/api/chat/threads`, {
      headers: {
        Authorization: `Bearer ${token.value}`,
      },
    });

    if (!response.ok) {
      throw new Error('Session verification failed');
    }

    const threadData = await response.json();

    console.log("threadData: ", threadData);

    return NextResponse.json(threadData, { status: 200 });
  } catch (error) {
    return NextResponse.json({ message: 'Not authenticated' }, { status: 401 });
  }
}
