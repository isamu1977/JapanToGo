<script lang="ts">
	import { Boxes, Scale } from 'lucide-svelte';
	import PhotoGallery from '#lib/components/ui/PhotoGallery.svelte';
	import { formatDateTime, formatWeight, statusTone } from '#lib/utils/formatters';
	import type { PageProps } from './$types';

	let { data }: PageProps = $props();

	const toneClasses: Record<string, string> = {
		green: 'bg-emerald-50 text-emerald-700',
		amber: 'bg-amber-50 text-amber-700',
		blue: 'bg-blue-50 text-blue-700',
		red: 'bg-red-50 text-red-700',
		gray: 'bg-slate-100 text-slate-600'
	};

	const statusLabels: Record<string, string> = {
		in_storage: 'Em estoque',
		consolidation_requested: 'Aguardando envio',
		shipped: 'Enviado',
		discarded: 'Descartado'
	};
</script>

<svelte:head>
	<title>Meus Pacotes - JapanToGo</title>
</svelte:head>

<header class="mb-6 flex flex-wrap items-center justify-between gap-3">
	<div>
		<h1 class="text-2xl font-bold text-ink-900">Meus Pacotes</h1>
		<p class="mt-1 text-sm text-slate-600">
			Itens recebidos no galpão, já pesados e inspecionados.
		</p>
	</div>
	<div class="flex gap-3 text-sm">
		<span class="rounded-xl bg-white px-3 py-2 shadow-sm ring-1 ring-slate-200">
			<Boxes size={14} class="mr-1 inline text-slate-400" />
			{data.suite.item_count} itens
		</span>
		<span class="rounded-xl bg-white px-3 py-2 shadow-sm ring-1 ring-slate-200">
			<Scale size={14} class="mr-1 inline text-slate-400" />
			{formatWeight(data.suite.total_weight_grams)}
		</span>
	</div>
</header>

{#if data.suite.items.length === 0}
	<div class="card p-10 text-center">
		<Boxes size={32} class="mx-auto text-slate-300" />
		<h2 class="mt-4 text-lg font-semibold text-ink-900">Seu Box está vazio</h2>
		<p class="mx-auto mt-2 max-w-md text-sm text-slate-600">
			Assim que um pacote com o código do seu Box for recebido e registrado pela nossa equipe, ele
			aparece aqui com peso e fotos.
		</p>
		<a href="/endereco" class="btn-secondary mt-6">Ver meu endereço</a>
	</div>
{:else}
	<ul class="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
		{#each data.suite.items as item (item.id)}
			<li class="card overflow-hidden">
				{#if item.photos.length > 0}
					<div class="border-b border-slate-100 p-3">
						<PhotoGallery photos={item.photos} alt={item.description} />
					</div>
				{/if}

				<div class="p-4">
					<h2 class="text-sm font-semibold text-ink-900">{item.description}</h2>

					<dl class="mt-3 space-y-1.5 text-sm">
						<div class="flex justify-between">
							<dt class="text-slate-500">Peso</dt>
							<dd class="font-medium text-ink-900">{formatWeight(item.weight_grams)}</dd>
						</div>
						<div class="flex justify-between">
							<dt class="text-slate-500">Recebido em</dt>
							<dd class="text-slate-700">{formatDateTime(item.received_at)}</dd>
						</div>
						{#if item.tracking_domestic}
							<div class="flex justify-between gap-2">
								<dt class="text-slate-500">Rastreio</dt>
								<dd class="truncate text-slate-700">{item.tracking_domestic}</dd>
							</div>
						{/if}
					</dl>

					<span class="badge mt-3 {toneClasses[statusTone(item.status)]}">
						{statusLabels[item.status] ?? item.status}
					</span>
				</div>
			</li>
		{/each}
	</ul>
{/if}
