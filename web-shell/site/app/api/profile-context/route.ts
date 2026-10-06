import { NextResponse } from 'next/server';
import { ProfileBindingError, resolveRuntimeProfileContext } from '@/lib/profile-context';

export async function GET() {
  try {
    const context = resolveRuntimeProfileContext();
    return NextResponse.json({
      profile_id: context.profileId,
      declared_repository: context.declaredRepository,
      runtime_repository: context.runtimeRepository,
      deployment_id: context.deploymentId,
      binding_state: context.bindingState,
      namespaces: {
        library: context.libraryPrefix,
        actions: context.actionPrefix,
        semantic_results: context.semanticResultPrefix,
      },
    });
  } catch (error) {
    if (error instanceof ProfileBindingError) {
      return NextResponse.json({
        binding_state: 'MISMATCH',
        error: error.message,
        code: 'PROFILE_BINDING_FAILED',
      }, { status: 409 });
    }
    throw error;
  }
}
