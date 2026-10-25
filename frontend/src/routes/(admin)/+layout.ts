import { redirect } from '@sveltejs/kit';
import { setFetchImplementation } from '#lib/api/client';
import { restoreSession } from '#lib/stores/auth';

/**
 * The admin portal is rendered in the browser only because the session lives
 * in an HTTP-only refresh cookie owned by the API origin.
 */
export const ssr = false;

export const load = async (event) => {
	setFetchImplementation(event.fetch);

	const profile = await restoreSession();

	if (!profile) {
		throw redirect(303, '/login');
	}

	if (profile.role !== 'admin') {
		throw redirect(303, profile.role === 'client' ? '/dashboard' : '/login');
	}

	return { profile };
};
