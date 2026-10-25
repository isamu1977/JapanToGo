<script lang="ts">
	import { CircleAlert, LoaderCircle, Package, Truck } from 'lucide-svelte';
	import { invalidateAll } from '$app/navigation';
	import { api } from '#lib/api/client';
	import type { PreOrder, PreOrderStatus, PreOrderType } from '#lib/api/types';
	import { formatJPY } from '#lib/utils/currency';
	import {
		PRE_ORDER_STATUS_LABELS,
		PRE_ORDER_TYPE_LABELS,
		formatDate
	} from '#lib/utils/formatters';
	import type { PageProps } from './$types';

	let { data }: PageProps = $props();

	let typeFilter = $state<PreOrderType | ''>('');
	let statusFilter = $state<PreOrderStatus | ''>('');

	let editing = $state<PreOrder | null>(null);
	let trackingCode = $state('');
	let adminNotes = $state('');
	let saving = $state(false);
	let failure = $state<string | null>(null);

	const filtered = $derived(
		data.preOrders.filter(
			(order) =>
				(typeFilter === '' || order.type === typeFilter) &&
				(statusFilter === '' || order.status === statusFilter)
		)
	);

	const toneClasses: Record<string, string> = {
		green: 'bg-emerald-50 text-emerald-700',
		amber: 'bg-amber-50 text-amber-700',
		blue: 'bg-blue-50 text-blue-700',
		red: 'bg-red-50 text-red-700',
		gray: 'bg-slate-100 text-slate-600'
	};

	function toneOf(status: string): string {
		if (status === 'received' || status === 'delivered') return 'green';
		if (status === 'submitted' || status === 'approved') return 'amber';
		if (status === 'purchased') return 'blue';
		if (status === 'cancelled') return 'red';
		return 'gray';
	}

	function openEditor(order: PreOrder) {
		editing = order;
		trackingCode = order.domestic_tracking_code ?? '';
		adminNotes = order.admin_notes ?? '';
		failure = null;
	}

	function closeEditor() {
		editing = null;
		failure = null;
	}

	async function savePurchase() {
		if (!editing) return;
		saving = true;
		failure = null;

		try {
			const updated = await api.put<PreOrder>(`/api/v1/admin/pre-orders/${editing.id}/purchase`, {
				status: 'purchased',
				domestic_tracking_code: trackingCode.trim() || null,
				admin_notes: adminNotes.trim() || null
			});
			data.preOrders = data.preOrders.map((order) => (order.id === updated.id ? updated : order));
			closeEditor();
			await invalidateAll();
		} catch (error) {
			failure = error instanceof Error ? error.message : 'Não foi possível salvar.';
		} finally {
			saving = false;
		}
	}
</script>

<svelte:head>
	<title>Pré-pedidos - Operação JapanToGo</title>
</svelte:head>

<header class="mb-6">
	<h1 class="text-2xl font-bold text-ink-900">Pré-pedidos</h1>
	<p class="mt-1 text-sm text-slate-600">Fila de compras assistidas e redirecionamentos.</p>
</header>

<div class="card mb-5 flex flex-wrap gap-3 p-4">
	<label class="block">
		<span class="label">Tipo</span>
		<select bind:value={typeFilter} class="input mt-1">
			<option value="">Todos</option>
			<option value="assisted_purchase">Compra assistida</option>
			<option value="forwarding">Redirecionamento</option>
		</select>
	</label>
	<label class="block">
		<span class="label">Status</span>
		<select bind:value={statusFilter} class="input mt-1">
			<option value="">Todos</option>
			{#each Object.entries(PRE_ORDER_STATUS_LABELS) as [value, label] (value)}
				<option {value}>{label.pt}</option>
			{/each}
		</select>
	</label>
</div>

{#if filtered.length === 0}
	<div class="card p-10 text-center">
		<Package size={32} class="mx-auto text-slate-300" />
		<p class="mt-4 text-sm text-slate-600">Nenhum pré-pedido com esses filtros.</p>
	</div>
{:else}
	<ul class="space-y-3">
		{#each filtered as order (order.id)}
			<li class="card p-5">
				<div class="flex flex-wrap items-start justify-between gap-3">
					<div class="min-w-0">
						<div class="flex flex-wrap items-center gap-2">
							<span class="badge {toneClasses[toneOf(order.status)]}">
								{PRE_ORDER_STATUS_LABELS[order.status].pt}
							</span>
							<span class="text-xs font-medium tracking-wide text-slate-400 uppercase">
								{PRE_ORDER_TYPE_LABELS[order.type].pt}
							</span>
						</div>

						<p class="mt-2 text-sm font-semibold text-ink-900">
							{order.type === 'forwarding'
								? (order.store_name ?? 'Redirecionamento')
								: `${order.items.length} ${order.items.length === 1 ? 'item' : 'itens'}`}
						</p>
						<p class="mt-0.5 text-xs text-slate-500">
							{formatDate(order.created_at)}
							{#if order.total_jpy > 0}
								· {formatJPY(order.total_jpy)}
							{/if}
							{#if order.domestic_tracking_code}
								· {order.domestic_tracking_code}
							{/if}
						</p>

						{#if order.type === 'assisted_purchase' && order.items.length > 0}
							<ul class="mt-2 space-y-0.5">
								{#each order.items as item (item.id)}
									<li class="truncate text-xs text-slate-500">
										· {item.product_name} × {item.quantity} — {formatJPY(item.line_total_jpy)}
									</li>
								{/each}
							</ul>
						{/if}
					</div>

					{#if order.type === 'assisted_purchase' && order.status === 'submitted'}
						<button type="button" onclick={() => openEditor(order)} class="btn-primary">
							<Truck size={15} /> Registrar compra
						</button>
					{/if}
				</div>
			</li>
		{/each}
	</ul>
{/if}

{#if editing}
	<div
		class="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/60 p-4"
		role="dialog"
		aria-modal="true"
		aria-label="Registrar compra"
		tabindex="-1"
	>
		<div class="w-full max-w-lg rounded-2xl bg-white p-6 shadow-xl">
			<h2 class="text-lg font-semibold text-ink-900">Registrar compra</h2>
			<p class="mt-1 text-sm text-slate-600">
				Informe o código de rastreio doméstico após a compra no Japão.
			</p>

			{#if failure}
				<p
					class="mt-4 flex items-start gap-2 rounded-xl bg-red-50 px-3 py-2.5 text-sm text-red-700"
				>
					<CircleAlert size={16} class="mt-0.5 shrink-0" />
					<span>{failure}</span>
				</p>
			{/if}

			<div class="mt-4 space-y-3">
				<label class="block">
					<span class="label">Rastreio doméstico</span>
					<input
						type="text"
						bind:value={trackingCode}
						class="input mt-1"
						placeholder="JP123456789012"
					/>
				</label>
				<label class="block">
					<span class="label">Observações internas</span>
					<textarea rows="3" bind:value={adminNotes} class="input mt-1"></textarea>
				</label>
			</div>

			<div class="mt-6 flex justify-end gap-2">
				<button type="button" onclick={closeEditor} class="btn-secondary">Cancelar</button>
				<button type="button" onclick={savePurchase} class="btn-primary" disabled={saving}>
					{#if saving}
						<LoaderCircle size={16} class="animate-spin" /> Salvando...
					{:else}
						Salvar
					{/if}
				</button>
			</div>
		</div>
	</div>
{/if}
