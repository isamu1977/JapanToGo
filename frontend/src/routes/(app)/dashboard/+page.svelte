<script lang="ts">
	import { ArrowRight, Boxes, MapPin, Package, Truck } from 'lucide-svelte';
	import { user } from '#lib/stores/auth';
	import { formatJPY } from '#lib/utils/currency';
	import {
		PRE_ORDER_STATUS_LABELS,
		PRE_ORDER_TYPE_LABELS,
		SHIPPING_METHOD_LABELS,
		SHIPMENT_STATUS_LABELS,
		SUITE_ITEM_STATUS_LABELS,
		formatDate,
		formatWeight,
		statusTone
	} from '#lib/utils/formatters';
	import type { PageProps } from './$types';

	let { data }: PageProps = $props();

	const activePreOrders = $derived(
		data.preOrders.filter((order) => !['received', 'cancelled'].includes(order.status))
	);
	const pendingShipments = $derived(
		data.shipments.filter((shipment) => ['requested', 'packed', 'paid'].includes(shipment.status))
	);

	const toneClasses: Record<string, string> = {
		green: 'bg-emerald-50 text-emerald-700',
		amber: 'bg-amber-50 text-amber-700',
		blue: 'bg-blue-50 text-blue-700',
		red: 'bg-red-50 text-red-700',
		gray: 'bg-slate-100 text-slate-600'
	};
</script>

<svelte:head>
	<title>Painel - JapanToGo</title>
</svelte:head>

<header class="mb-6">
	<h1 class="text-2xl font-bold text-ink-900">Olá, {$user?.full_name?.split(' ')[0] ?? ''}</h1>
	<p class="mt-1 text-sm text-slate-600">Acompanhe seus pedidos, itens no seu Box e envios.</p>
</header>

<section class="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
	<a href="/pre-pedidos" class="card p-5 transition hover:border-brand-300">
		<div class="flex items-center justify-between">
			<span
				class="flex h-10 w-10 items-center justify-center rounded-xl bg-brand-50 text-brand-600"
			>
				<Package size={20} />
			</span>
			<ArrowRight size={16} class="text-slate-300" />
		</div>
		<p class="mt-4 text-3xl font-bold text-ink-900">{activePreOrders.length}</p>
		<p class="text-sm text-slate-500">Pré-pedidos ativos</p>
	</a>

	<a href="/suite" class="card p-5 transition hover:border-brand-300">
		<div class="flex items-center justify-between">
			<span class="flex h-10 w-10 items-center justify-center rounded-xl bg-blue-50 text-blue-600">
				<Boxes size={20} />
			</span>
			<ArrowRight size={16} class="text-slate-300" />
		</div>
		<p class="mt-4 text-3xl font-bold text-ink-900">{data.suite.item_count}</p>
		<p class="text-sm text-slate-500">
			Itens no seu Box ({formatWeight(data.suite.total_weight_grams)})
		</p>
	</a>

	<a href="/envios" class="card p-5 transition hover:border-brand-300">
		<div class="flex items-center justify-between">
			<span
				class="flex h-10 w-10 items-center justify-center rounded-xl bg-amber-50 text-amber-600"
			>
				<Truck size={20} />
			</span>
			<ArrowRight size={16} class="text-slate-300" />
		</div>
		<p class="mt-4 text-3xl font-bold text-ink-900">{pendingShipments.length}</p>
		<p class="text-sm text-slate-500">Envios pendentes</p>
	</a>

	<a href="/endereco" class="card p-5 transition hover:border-brand-300">
		<div class="flex items-center justify-between">
			<span
				class="flex h-10 w-10 items-center justify-center rounded-xl bg-emerald-50 text-emerald-600"
			>
				<MapPin size={20} />
			</span>
			<ArrowRight size={16} class="text-slate-300" />
		</div>
		<p class="mt-4 font-mono text-2xl font-bold text-ink-900">{data.suite.suite_code ?? '—'}</p>
		<p class="text-sm text-slate-500">Código do seu Box</p>
	</a>
</section>

<section class="mt-8 grid gap-6 lg:grid-cols-2">
	<div class="card p-5">
		<div class="flex items-center justify-between">
			<h2 class="text-base font-semibold text-ink-900">Pré-pedidos recentes</h2>
			<a href="/pre-pedidos" class="text-sm font-medium text-brand-700 hover:underline">Ver todos</a
			>
		</div>

		{#if data.preOrders.length === 0}
			<p class="mt-4 text-sm text-slate-500">
				Nenhum pré-pedido ainda. Crie uma compra assistida ou um redirecionamento.
			</p>
		{:else}
			<ul class="mt-4 divide-y divide-slate-100">
				{#each data.preOrders.slice(0, 5) as order (order.id)}
					<li class="flex items-center justify-between gap-3 py-3">
						<div class="min-w-0">
							<p class="truncate text-sm font-medium text-ink-900">
								{PRE_ORDER_TYPE_LABELS[order.type].pt}
								{#if order.store_name}
									<span class="font-normal text-slate-500">· {order.store_name}</span>
								{/if}
							</p>
							<p class="text-xs text-slate-400">
								{formatDate(order.created_at)}
								{#if order.total_jpy > 0}
									· {formatJPY(order.total_jpy)}
								{/if}
							</p>
						</div>
						<span class="badge {toneClasses[statusTone(order.status)]}">
							{PRE_ORDER_STATUS_LABELS[order.status].pt}
						</span>
					</li>
				{/each}
			</ul>
		{/if}
	</div>

	<div class="card p-5">
		<div class="flex items-center justify-between">
			<h2 class="text-base font-semibold text-ink-900">Envios</h2>
			<a href="/envios" class="text-sm font-medium text-brand-700 hover:underline">Ver todos</a>
		</div>

		{#if data.shipments.length === 0}
			<p class="mt-4 text-sm text-slate-500">
				Nenhum envio ainda. Consolide os itens do seu Box para enviar ao Brasil.
			</p>
		{:else}
			<ul class="mt-4 divide-y divide-slate-100">
				{#each data.shipments.slice(0, 5) as shipment (shipment.id)}
					<li class="flex items-center justify-between gap-3 py-3">
						<div class="min-w-0">
							<p class="truncate text-sm font-medium text-ink-900">
								{SHIPPING_METHOD_LABELS[shipment.shipping_method].pt}
							</p>
							<p class="text-xs text-slate-400">
								{formatDate(shipment.created_at)} · {formatWeight(shipment.total_weight_grams)}
								{#if shipment.international_tracking_code}
									· {shipment.international_tracking_code}
								{/if}
							</p>
						</div>
						<span class="badge {toneClasses[statusTone(shipment.status)]}">
							{SHIPMENT_STATUS_LABELS[shipment.status].pt}
						</span>
					</li>
				{/each}
			</ul>
		{/if}
	</div>
</section>

<section class="card mt-6 p-5">
	<h2 class="text-base font-semibold text-ink-900">Itens no seu Box</h2>
	{#if data.suite.items.length === 0}
		<p class="mt-3 text-sm text-slate-500">
			Seu Box está vazio. Assim que a equipe do galpão fizer o check-in dos seus pacotes, eles
			aparecerão aqui.
		</p>
	{:else}
		<ul class="mt-4 grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
			{#each data.suite.items.slice(0, 6) as item (item.id)}
				<li class="rounded-xl border border-slate-200 p-3">
					<p class="truncate text-sm font-medium text-ink-900">{item.description}</p>
					<p class="mt-1 text-xs text-slate-500">{formatWeight(item.weight_grams)}</p>
					<span class="badge mt-2 {toneClasses[statusTone(item.status)]}">
						{SUITE_ITEM_STATUS_LABELS[item.status].pt}
					</span>
				</li>
			{/each}
		</ul>
	{/if}
</section>
