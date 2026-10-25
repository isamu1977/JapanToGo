import { redirect } from '@sveltejs/kit';
import { setFetchImplementation } from '#lib/api/client';
import { restoreSession } from '#lib/stores/auth';

/**
 * The client area is rendered in the browser only: the session lives in an
 * HTTP-only refresh cookie owned by the API origin, so the server cannot
 * read it. `ssr = false` guarantees the guard always runs in the browser.
 */
export const ssr = false;

export const load = async (event) => {
	setFetchImplementation(event.fetch);

	const profile = await restoreSession();

	if (!profile) {
		throw redirect(303, '/login');
	}

	if (profile.role !== 'client') {
		throw redirect(303, profile.role === 'admin' ? '/admin/dashboard' : '/login');
	}

	return { profile };
};
