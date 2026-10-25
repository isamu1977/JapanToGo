<script lang="ts">
	import { Boxes, ClipboardCheck, Package, Truck, Users } from 'lucide-svelte';
	import { formatWeight } from '#lib/utils/formatters';
	import type { PageProps } from './$types';

	let { data }: PageProps = $props();

	const dashboard = $derived(data.dashboard);

	const actions = $derived([
		{
			href: '/admin/pre-pedidos',
			label: 'Compras a concluir',
			value: dashboard.pending_actions.purchases_to_complete,
			icon: Package,
			tone: 'bg-amber-50 text-amber-600'
		},
		{
			href: '/admin/warehouse-checkin',
			label: 'Pacotes para check-in',
			value: dashboard.pending_actions.packages_to_check_in,
			icon: ClipboardCheck,
			tone: 'bg-blue-50 text-blue-600'
		},
		{
			href: '/admin/envios',
			label: 'Envios para despachar',
			value: dashboard.pending_actions.shipments_to_dispatch,
			icon: Truck,
			tone: 'bg-brand-50 text-brand-600'
		}
	]);
</script>

<svelte:head>
	<title>Painel operacional - JapanToGo</title>
</svelte:head>

<header class="mb-6">
	<h1 class="text-2xl font-bold text-ink-900">Painel operacional</h1>
	<p class="mt-1 text-sm text-slate-600">Visão geral da operação no galpão japonês.</p>
</header>

<section class="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
	<div class="card p-5">
		<span class="flex h-10 w-10 items-center justify-center rounded-xl bg-slate-100 text-slate-600">
			<Users size={20} />
		</span>
		<p class="mt-4 text-3xl font-bold text-ink-900">{dashboard.clients}</p>
		<p class="text-sm text-slate-500">Clientes cadastrados</p>
	</div>

	<div class="card p-5">
		<span class="flex h-10 w-10 items-center justify-center rounded-xl bg-amber-50 text-amber-600">
			<Package size={20} />
		</span>
		<p class="mt-4 text-3xl font-bold text-ink-900">{dashboard.pre_orders.total}</p>
		<p class="text-sm text-slate-500">Pré-pedidos</p>
	</div>

	<div class="card p-5">
		<span class="flex h-10 w-10 items-center justify-center rounded-xl bg-blue-50 text-blue-600">
			<Boxes size={20} />
		</span>
		<p class="mt-4 text-3xl font-bold text-ink-900">{dashboard.suite_items.total}</p>
		<p class="text-sm text-slate-500">
			Itens em estoque ({formatWeight(dashboard.suite_items.stored_weight_grams)})
		</p>
	</div>

	<div class="card p-5">
		<span class="flex h-10 w-10 items-center justify-center rounded-xl bg-brand-50 text-brand-600">
			<Truck size={20} />
		</span>
		<p class="mt-4 text-3xl font-bold text-ink-900">{dashboard.shipments.total}</p>
		<p class="text-sm text-slate-500">Envios</p>
	</div>
</section>

<section class="mt-8">
	<h2 class="text-lg font-semibold text-ink-900">Ações pendentes</h2>
	<div class="mt-4 grid gap-4 sm:grid-cols-3">
		{#each actions as action (action.href)}
			<a
				href={action.href}
				class="card flex items-center gap-4 p-5 transition hover:border-brand-300"
			>
				<span class="flex h-11 w-11 items-center justify-center rounded-xl {action.tone}">
					<action.icon size={22} />
				</span>
				<span>
					<span class="block text-2xl font-bold text-ink-900">{action.value}</span>
					<span class="block text-sm text-slate-500">{action.label}</span>
				</span>
			</a>
		{/each}
	</div>
</section>

<section class="mt-8 grid gap-6 lg:grid-cols-3">
	<div class="card p-5">
		<h2 class="text-sm font-semibold tracking-wide text-slate-500 uppercase">
			Pré-pedidos por status
		</h2>
		<ul class="mt-4 space-y-2 text-sm">
			{#each Object.entries(dashboard.pre_orders.by_status) as [status, count] (status)}
				<li class="flex justify-between">
					<span class="text-slate-600">{status}</span>
					<span class="font-medium text-ink-900">{count}</span>
				</li>
			{/each}
			{#if Object.keys(dashboard.pre_orders.by_status).length === 0}
				<li class="text-slate-400">Nenhum pré-pedido.</li>
			{/if}
		</ul>
	</div>

	<div class="card p-5">
		<h2 class="text-sm font-semibold tracking-wide text-slate-500 uppercase">Itens por status</h2>
		<ul class="mt-4 space-y-2 text-sm">
			{#each Object.entries(dashboard.suite_items.by_status) as [status, count] (status)}
				<li class="flex justify-between">
					<span class="text-slate-600">{status}</span>
					<span class="font-medium text-ink-900">{count}</span>
				</li>
			{/each}
			{#if Object.keys(dashboard.suite_items.by_status).length === 0}
				<li class="text-slate-400">Nenhum item.</li>
			{/if}
		</ul>
	</div>

	<div class="card p-5">
		<h2 class="text-sm font-semibold tracking-wide text-slate-500 uppercase">Envios por status</h2>
		<ul class="mt-4 space-y-2 text-sm">
			{#each Object.entries(dashboard.shipments.by_status) as [status, count] (status)}
				<li class="flex justify-between">
					<span class="text-slate-600">{status}</span>
					<span class="font-medium text-ink-900">{count}</span>
				</li>
			{/each}
			{#if Object.keys(dashboard.shipments.by_status).length === 0}
				<li class="text-slate-400">Nenhum envio.</li>
			{/if}
		</ul>
	</div>
</section>
