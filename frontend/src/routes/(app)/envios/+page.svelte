<script lang="ts">
	import { Plus, Truck } from 'lucide-svelte';
	import { formatJPY } from '#lib/utils/currency';
	import {
		SHIPPING_METHOD_LABELS,
		SHIPMENT_STATUS_LABELS,
		formatDate,
		formatWeight,
		maskCpf,
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
	<title>Envios - JapanToGo</title>
</svelte:head>

<header class="mb-6 flex flex-wrap items-center justify-between gap-3">
	<div>
		<h1 class="text-2xl font-bold text-ink-900">Envios</h1>
		<p class="mt-1 text-sm text-slate-600">
			Consolide seus itens e acompanhe o transporte internacional.
		</p>
	</div>
	<a href="/envios/novo" class="btn-primary"><Plus size={16} /> Novo envio</a>
</header>

{#if data.shipments.length === 0}
	<div class="card p-10 text-center">
		<Truck size={32} class="mx-auto text-slate-300" />
		<h2 class="mt-4 text-lg font-semibold text-ink-900">Nenhum envio ainda</h2>
		<p class="mx-auto mt-2 max-w-md text-sm text-slate-600">
			Selecione os itens que estão no seu Box, escolha EMS ou Small Packet e informe a declaração
			aduaneira.
		</p>
		<a href="/envios/novo" class="btn-primary mt-6">Criar envio</a>
	</div>
{:else}
	<ul class="space-y-4">
		{#each data.shipments as shipment (shipment.id)}
			<li class="card p-5">
				<div class="flex flex-wrap items-start justify-between gap-3">
					<div>
						<div class="flex flex-wrap items-center gap-2">
							<span class="badge {toneClasses[statusTone(shipment.status)]}">
								{SHIPMENT_STATUS_LABELS[shipment.status].pt}
							</span>
							<span class="text-xs font-medium tracking-wide text-slate-400 uppercase">
								{SHIPPING_METHOD_LABELS[shipment.shipping_method].pt}
							</span>
						</div>

						<p class="mt-2 text-sm font-semibold text-ink-900">
							{shipment.recipient_name} · {maskCpf(shipment.recipient_cpf)}
						</p>
						<p class="mt-0.5 text-xs text-slate-500">
							{formatDate(shipment.created_at)} · {formatWeight(shipment.total_weight_grams)}
							{#if shipment.shipping_fee_jpy > 0}
								· frete {formatJPY(shipment.shipping_fee_jpy)}
							{/if}
						</p>
						{#if shipment.international_tracking_code}
							<p class="mt-1 font-mono text-xs text-brand-700">
								{shipment.international_tracking_code}
							</p>
						{/if}
					</div>

					{#if shipment.customs_declaration && shipment.customs_declaration.items.length > 0}
						<div class="rounded-xl bg-slate-50 px-4 py-3 text-right">
							<p class="text-xs text-slate-500">Valor declarado</p>
							<p class="text-sm font-semibold text-ink-900">
								{formatJPY(shipment.customs_declaration.total_declared_value_jpy ?? 0)}
							</p>
							<p class="text-xs text-slate-500">
								{shipment.customs_declaration.items.length} linhas
							</p>
						</div>
					{/if}
				</div>
			</li>
		{/each}
	</ul>
{/if}
