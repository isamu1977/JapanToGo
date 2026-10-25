import { loadApi } from '#lib/api/load';
import type { PreOrder } from '#lib/api/types';

export const load = async (event) => {
	const preOrders = await loadApi<PreOrder[]>(event, '/api/v1/pre-orders');
	return { preOrders };
};
