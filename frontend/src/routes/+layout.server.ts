import { PUBLIC_API_BASE_URL } from '$app/env/public';

/**
 * The public API base URL is resolved on the server (adapter-node reads the
 * environment at runtime) and handed to the browser through the root layout,
 * so a single Docker image works in every environment.
 */
export const load = async () => {
	return {
		apiBaseUrl: PUBLIC_API_BASE_URL ?? ''
	};
};
