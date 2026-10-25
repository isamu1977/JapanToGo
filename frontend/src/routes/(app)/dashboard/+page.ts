import { loadApi } from '#lib/api/load';
import type { PreOrder, Shipment, SuiteSummary } from '#lib/api/types';

export const load = async (event) => {
	const [suite, preOrders, shipments] = await Promise.all([
		loadApi<SuiteSummary>(event, '/api/v1/suite/me'),
		loadApi<PreOrder[]>(event, '/api/v1/pre-orders'),
		loadApi<Shipment[]>(event, '/api/v1/shipments')
	]);

	return { suite, preOrders, shipments };
};
