<script lang="ts">
	import { ArrowRight, Package, Plus, Truck } from 'lucide-svelte';
	import { formatJPY } from '#lib/utils/currency';
	import {
		PRE_ORDER_STATUS_LABELS,
		PRE_ORDER_TYPE_LABELS,
		formatDate,
		orDash,
		statusTone
	} from '#lib/utils/formatters';
	import type { PageProps } from './$types';

	let { data }: PageProps = $props();

	const toneClasses: Record<string, string> = {
		green: 'bg-emerald-50 text-emerald-700',
		amber: 'bg-amber-50 text-amber-700',
		blue: 'bg-blue-50 text-blue-700',
		red: 'bg-red-50 text-red-700',
		gray: 'bg-slate-100 text-slate-600'
	};
</script>

<svelte:head>
	<title>Pré-pedidos - JapanToGo</title>
</svelte:head>

<header class="mb-6 flex flex-wrap items-center justify-between gap-3">
	<div>
		<h1 class="text-2xl font-bold text-ink-900">Pré-pedidos</h1>
		<p class="mt-1 text-sm text-slate-600">Suas compras assistidas e redirecionamentos.</p>
	</div>
	<div class="flex flex-wrap gap-2">
		<a href="/pre-pedidos/novo-assistida" class="btn-primary">
			<Plus size={16} /> Compra assistida
		</a>
		<a href="/pre-pedidos/novo-redirecionamento" class="btn-secondary">
			<Truck size={16} /> Redirecionamento
		</a>
	</div>
</header>

{#if data.preOrders.length === 0}
	<div class="card p-10 text-center">
		<Package size={32} class="mx-auto text-slate-300" />
		<h2 class="mt-4 text-lg font-semibold text-ink-900">Nenhum pré-pedido ainda</h2>
		<p class="mx-auto mt-2 max-w-md text-sm text-slate-600">
			Envie os links dos produtos para nós comprarmos (compra assistida) ou registe um
			redirecionamento de um pacote que você já comprou no Japão.
		</p>
		<div class="mt-6 flex flex-wrap justify-center gap-2">
			<a href="/pre-pedidos/novo-assistida" class="btn-primary">Criar compra assistida</a>
			<a href="/pre-pedidos/novo-redirecionamento" class="btn-secondary">Criar redirecionamento</a>
		</div>
	</div>
{:else}
	<ul class="space-y-4">
		{#each data.preOrders as order (order.id)}
			<li class="card p-5">
				<div class="flex flex-wrap items-start justify-between gap-3">
					<div class="min-w-0">
						<div class="flex flex-wrap items-center gap-2">
							<span class="badge {toneClasses[statusTone(order.status)]}">
								{PRE_ORDER_STATUS_LABELS[order.status].pt}
							</span>
							<span class="text-xs font-medium tracking-wide text-slate-400 uppercase">
								{PRE_ORDER_TYPE_LABELS[order.type].pt}
							</span>
						</div>
						<p class="mt-2 text-sm font-semibold text-ink-900">
							{order.type === 'forwarding'
								? orDash(order.store_name)
								: `${order.items.length} ${order.items.length === 1 ? 'item' : 'itens'}`}
						</p>
						<p class="mt-0.5 text-xs text-slate-500">
							Criado em {formatDate(order.created_at)}
							{#if order.domestic_tracking_code}
								· Tracking {order.domestic_tracking_code}
							{/if}
							{#if order.expected_domestic_tracking && !order.domestic_tracking_code}
								· Tracking esperado {order.expected_domestic_tracking}
							{/if}
						</p>
					</div>

					<div class="text-right">
						{#if order.total_jpy > 0}
							<p class="text-lg font-bold text-ink-900">{formatJPY(order.total_jpy)}</p>
							<p class="text-xs text-slate-500">
								Itens {formatJPY(order.total_items_price_jpy)} · taxa {formatJPY(
									order.service_fee_jpy
								)}
							</p>
						{:else}
							<p class="text-sm text-slate-500">Aguardando cotação</p>
						{/if}
					</div>
				</div>

				{#if order.type === 'assisted_purchase' && order.items.length > 0}
					<ul class="mt-4 space-y-1 border-t border-slate-100 pt-3">
						{#each order.items as item (item.id)}
							<li class="flex items-baseline justify-between gap-3 text-sm">
								<a
									href={item.product_url}
									target="_blank"
									rel="noreferrer noopener"
									class="truncate text-slate-700 hover:text-brand-700 hover:underline"
								>
									{item.product_name} × {item.quantity}
								</a>
								<span class="shrink-0 text-xs text-slate-500">
									{formatJPY(item.line_total_jpy)}
								</span>
							</li>
						{/each}
					</ul>
				{/if}

				{#if order.receipt_url}
					<p class="mt-3 text-xs text-slate-500">
						Comprovante: <a
							href={order.receipt_url}
							class="text-brand-700 underline"
							target="_blank">{order.receipt_filename ?? 'ver arquivo'}</a
						>
					</p>
				{/if}
			</li>
		{/each}
	</ul>

	<p class="mt-6 flex items-center gap-2 text-sm text-slate-500">
		<ArrowRight size={14} /> Novas encomendas aparecem em “Meus Pacotes” após o check-in no galpão, com
		o status “Item recebido no seu Box”.
	</p>
{/if}
