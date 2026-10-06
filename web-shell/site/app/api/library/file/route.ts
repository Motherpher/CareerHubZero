import { get } from '@vercel/blob';
import { NextResponse } from 'next/server';
import { assertProfileOwnedPath, ProfileBindingError, resolveRuntimeProfileContext } from '@/lib/profile-context';

export async function GET(request: Request) {
  try {
    const context = resolveRuntimeProfileContext();
    const { searchParams } = new URL(request.url);
    const pathname = searchParams.get('pathname') ?? '';
    assertProfileOwnedPath(pathname, context.libraryPrefix);
    const result = await get(pathname, { access: 'private' });
    if (result?.statusCode !== 200) return new NextResponse('Not found', { status: 404 });
    return new NextResponse(result.stream, {
      headers: {
        'Content-Type': result.blob.contentType,
        'X-Content-Type-Options': 'nosniff',
        'X-CareerHub-Profile': context.profileId,
      }
    });
  } catch (error) {
    if (error instanceof ProfileBindingError) {
      return NextResponse.json({ error: error.message, code: 'PROFILE_BINDING_FAILED' }, { status: 409 });
    }
    throw error;
  }
}
