import { loadApi } from '#lib/api/load';
import type { Shipment } from '#lib/api/types';

export const load = async (event) => {
	const shipments = await loadApi<Shipment[]>(event, '/api/v1/shipments');
	return { shipments };
};
