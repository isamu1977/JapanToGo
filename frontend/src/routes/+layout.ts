import { setApiBaseUrl } from '#lib/config';
import type { LayoutLoad } from './$types';

/**
 * Configure the API base URL as early as possible.
 *
 * The root universal load runs before every nested load, so the API client
 * already knows where the backend lives when the authentication guard of the
 * `(app)` / `(admin)` groups executes.
 */
export const load: LayoutLoad = async ({ data }) => {
	setApiBaseUrl(data.apiBaseUrl);
	return {};
};
