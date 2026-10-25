import { loadApi } from '#lib/api/load';
import type { SuiteSummary } from '#lib/api/types';

export const load = async (event) => {
	const suite = await loadApi<SuiteSummary>(event, '/api/v1/suite/me');
	return { suite };
};
