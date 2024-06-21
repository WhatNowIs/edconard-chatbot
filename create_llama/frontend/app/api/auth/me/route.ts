import { getBackendURL } from '@/app/service/utils';
import { NextResponse, NextRequest } from 'next/server';

export async function GET(req: NextRequest) {
  const token = req.cookies.get('access_token');

  if (!token) {
    return NextResponse.json({ message: 'Not authenticated' }, { status: 401 });
  }

  try {
    const response = await fetch(`${getBackendURL()}/api/auth/accounts/me`, {
      headers: {
        Authorization: `Bearer ${token.value}`,
      },
    });

    if (!response.ok) {
      throw new Error('Session verification failed');
    }

    const userData = await response.json();

    console.log(userData);

    return NextResponse.json(userData, { status: 200 });
  } catch (error) {
    return NextResponse.json({ message: 'Not authenticated' }, { status: 401 });
  }
}
