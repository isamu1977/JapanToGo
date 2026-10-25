import { loadApi } from '#lib/api/load';
import type { WarehouseAddress } from '#lib/api/types';

export const load = async (event) => {
	const address = await loadApi<WarehouseAddress>(event, '/api/v1/suite/me/address');
	return { address };
};
