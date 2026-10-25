import { defineEnvVars } from '@sveltejs/kit/env';

/**
 * Environment variables consumed by the application.
 *
 * `PUBLIC_API_BASE_URL` is public (safe to expose to the browser) and not
 * static, so it is read from the environment when the app starts. This keeps
 * a single Docker image usable in every environment (local, staging, Coolify)
 * without rebuilding the frontend.
 */
export const variables = defineEnvVars({
	PUBLIC_API_BASE_URL: {
		public: true,
		static: false,
		description: 'Base URL of the FastAPI backend (empty means same origin).',
		schema: (value) => value ?? ''
	}
});
