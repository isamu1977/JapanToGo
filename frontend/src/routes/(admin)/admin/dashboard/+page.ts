import { loadApi } from '#lib/api/load';
import type { AdminDashboard } from '#lib/api/types';

export const load = async (event) => {
	const dashboard = await loadApi<AdminDashboard>(event, '/api/v1/admin/dashboard');
	return { dashboard };
};
