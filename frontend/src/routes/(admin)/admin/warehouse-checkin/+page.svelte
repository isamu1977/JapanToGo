<script lang="ts">
	import { CircleAlert, LoaderCircle, Scale, Search, Upload } from 'lucide-svelte';
	import { api } from '#lib/api/client';
	import type { AdminWarehouseSearchResult, SuiteItem } from '#lib/api/types';
	import { formatDate } from '#lib/utils/formatters';

	let query = $state('');
	let results = $state<AdminWarehouseSearchResult[]>([]);
	let searching = $state(false);
	let searchError = $state<string | null>(null);

	let selected = $state<AdminWarehouseSearchResult | null>(null);
	let description = $state('');
	let weightGrams = $state<number | null>(null);
	let trackingDomestic = $state('');
	let preOrderId = $state('');
	let photos = $state<File[]>([]);
	let saving = $state(false);
	let failure = $state<string | null>(null);
	let success = $state<string | null>(null);

	const MAX_PHOTOS = 5;

	async function search(event?: SubmitEvent) {
		event?.preventDefault();
		if (query.trim().length === 0) return;

		searching = true;
		searchError = null;
		try {
			results = await api.get<AdminWarehouseSearchResult[]>(
				`/api/v1/admin/warehouse/search?q=${encodeURIComponent(query.trim())}`
			);
			if (results.length === 1) selectClient(results[0]);
		} catch (error) {
			searchError = error instanceof Error ? error.message : 'Falha na busca.';
			results = [];
		} finally {
			searching = false;
		}
	}

	function selectClient(client: AdminWarehouseSearchResult) {
		selected = client;
		success = null;
		failure = null;
	}

	function onPhotosChange(event: Event) {
		const input = event.currentTarget as HTMLInputElement;
		const files = Array.from(input.files ?? []);
		photos = files.slice(0, MAX_PHOTOS);
	}

	async function checkin(event: SubmitEvent) {
		event.preventDefault();
		if (!selected) return;

		failure = null;
		success = null;

		if (!description.trim()) {
			failure = 'Informe a descrição do pacote.';
			return;
		}
		if (!weightGrams || weightGrams <= 0) {
			failure = 'Informe o peso em gramas.';
			return;
		}
		if (photos.length === 0) {
			failure = 'Anexe ao menos uma foto de inspeção.';
			return;
		}

		saving = true;
		try {
			const body = new FormData();
			body.append('suite_code', selected.suite_code ?? '');
			body.append('description', description.trim());
			body.append('weight_grams', String(weightGrams));
			if (trackingDomestic.trim()) body.append('tracking_domestic', trackingDomestic.trim());
			if (preOrderId.trim()) body.append('pre_order_id', preOrderId.trim());
			for (const photo of photos) body.append('photos', photo);

			await api.postForm<SuiteItem>('/api/v1/admin/warehouse/checkin', body);

			success = `Item registrado para ${selected.suite_code}.`;
			description = '';
			weightGrams = null;
			trackingDomestic = '';
			preOrderId = '';
			photos = [];
			selected = null;
			query = '';
			results = [];
		} catch (error) {
			failure = error instanceof Error ? error.message : 'Não foi possível registrar o item.';
		} finally {
			saving = false;
		}
	}
</script>

<svelte:head>
	<title>Check-in do galpão - Operação JapanToGo</title>
</svelte:head>

<header class="mb-6">
	<h1 class="text-2xl font-bold text-ink-900">Check-in rápido</h1>
	<p class="mt-1 text-sm text-slate-600">
		Busque o cliente pelo código de suíte, pese o pacote e registre as fotos de inspeção.
	</p>
</header>

<section class="card p-5">
	<form onsubmit={search} class="flex flex-wrap gap-3">
		<label class="min-w-56 flex-1">
			<span class="label">Código de suíte ou nome</span>
			<input
				type="search"
				bind:value={query}
				class="input mt-1"
				placeholder="JTG-1001"
				autocomplete="off"
			/>
		</label>
		<button type="submit" class="btn-primary self-end" disabled={searching}>
			{#if searching}
				<LoaderCircle size={16} class="animate-spin" /> Buscando...
			{:else}
				<Search size={16} /> Buscar
			{/if}
		</button>
	</form>

	{#if searchError}
		<p class="mt-4 flex items-start gap-2 rounded-xl bg-red-50 px-3 py-2.5 text-sm text-red-700">
			<CircleAlert size={16} class="mt-0.5 shrink-0" />
			<span>{searchError}</span>
		</p>
	{/if}

	{#if results.length > 0}
		<ul class="mt-4 grid gap-2 sm:grid-cols-2">
			{#each results as client (client.id)}
				<li>
					<button
						type="button"
						onclick={() => selectClient(client)}
						class="w-full rounded-xl border p-3 text-left transition {selected?.id === client.id
							? 'border-brand-300 bg-brand-50'
							: 'border-slate-200 hover:bg-slate-50'}"
					>
						<span class="block font-mono text-sm font-bold text-brand-700">
							{client.suite_code ?? '—'}
						</span>
						<span class="block text-sm text-ink-900">{client.full_name}</span>
						<span class="block text-xs text-slate-500">
							{client.pending_pre_orders.length} pré-pedido(s) pendente(s)
						</span>
					</button>
				</li>
			{/each}
		</ul>
	{/if}
</section>

{#if success}
	<p class="mt-6 rounded-xl bg-emerald-50 px-4 py-3 text-sm text-emerald-700" role="status">
		{success}
	</p>
{/if}

{#if selected}
	<form class="card mt-6 p-5" onsubmit={checkin}>
		<h2 class="text-base font-semibold text-ink-900">
			Novo item para <span class="font-mono text-brand-700">{selected.suite_code}</span>
		</h2>
		<p class="mt-1 text-sm text-slate-600">{selected.full_name} · {selected.email}</p>

		{#if selected.pending_pre_orders.length > 0}
			<div class="mt-4 rounded-xl bg-slate-50 p-3">
				<p class="text-xs font-semibold tracking-wide text-slate-500 uppercase">
					Pré-pedidos pendentes
				</p>
				<ul class="mt-2 space-y-1 text-sm">
					{#each selected.pending_pre_orders as order (order.id)}
						<li class="flex items-center justify-between gap-3">
							<span class="min-w-0 truncate text-slate-700">
								{order.store_name ?? order.type} · {formatDate(order.created_at)}
								{#if order.expected_domestic_tracking}
									· {order.expected_domestic_tracking}
								{/if}
							</span>
							<button
								type="button"
								onclick={() => (preOrderId = order.id)}
								class="shrink-0 rounded-lg border border-slate-300 px-2 py-1 text-xs font-medium text-slate-700 hover:border-brand-300 hover:text-brand-700"
							>
								Vincular
							</button>
						</li>
					{/each}
				</ul>
				{#if preOrderId}
					<p class="mt-2 text-xs text-brand-700">Pré-pedido vinculado: {preOrderId}</p>
				{/if}
			</div>
		{/if}

		<div class="mt-4 grid gap-3 sm:grid-cols-2">
			<label class="block">
				<span class="label">Descrição do pacote</span>
				<input
					type="text"
					required
					bind:value={description}
					class="input mt-1"
					placeholder="Caixa de sapatos Nike"
				/>
			</label>

			<label class="block">
				<span class="label">Peso (gramas)</span>
				<span class="relative mt-1 block">
					<Scale size={16} class="absolute top-2.5 left-3 text-slate-400" />
					<input
						type="number"
						required
						min="1"
						step="1"
						bind:value={weightGrams}
						class="input pl-9"
						placeholder="1450"
					/>
				</span>
			</label>

			<label class="block sm:col-span-2">
				<span class="label">Rastreio doméstico</span>
				<input
					type="text"
					bind:value={trackingDomestic}
					class="input mt-1"
					placeholder="123456789012"
				/>
			</label>
		</div>

		<div class="mt-4">
			<span class="label">Fotos de inspeção (até {MAX_PHOTOS})</span>
			<label
				class="mt-1 flex cursor-pointer flex-col items-center justify-center gap-2 rounded-xl border-2 border-dashed border-slate-300 bg-slate-50 px-4 py-6 text-center transition hover:border-brand-300 hover:bg-brand-50/40"
			>
				<input
					type="file"
					accept="image/png,image/jpeg,image/webp"
					multiple
					class="sr-only"
					onchange={onPhotosChange}
				/>
				<Upload size={24} class="text-slate-400" />
				<span class="text-sm font-medium text-ink-900">
					{photos.length > 0
						? `${photos.length} foto(s) selecionada(s)`
						: 'Toque para capturar ou enviar fotos'}
				</span>
				<span class="text-xs text-slate-500">JPG, PNG ou WebP · até 5 MB cada</span>
			</label>

			{#if photos.length > 0}
				<ul class="mt-3 grid grid-cols-5 gap-2">
					{#each photos as photo, index (photo.name + index)}
						<li class="relative">
							<img
								src={URL.createObjectURL(photo)}
								alt={photo.name}
								class="aspect-square w-full rounded-lg object-cover"
							/>
							<button
								type="button"
								onclick={() => (photos = photos.filter((_, i) => i !== index))}
								class="absolute -top-1.5 -right-1.5 flex h-5 w-5 items-center justify-center rounded-full bg-red-600 text-xs text-white"
								aria-label="Remover foto"
							>
								×
							</button>
						</li>
					{/each}
				</ul>
			{/if}
		</div>

		{#if failure}
			<p
				class="mt-4 flex items-start gap-2 rounded-xl bg-red-50 px-3 py-2.5 text-sm text-red-700"
				role="alert"
			>
				<CircleAlert size={16} class="mt-0.5 shrink-0" />
				<span>{failure}</span>
			</p>
		{/if}

		<div class="mt-5 flex justify-end gap-2">
			<button
				type="button"
				onclick={() => {
					selected = null;
					failure = null;
				}}
				class="btn-secondary"
			>
				Cancelar
			</button>
			<button type="submit" class="btn-primary" disabled={saving}>
				{#if saving}
					<LoaderCircle size={16} class="animate-spin" /> Registrando...
				{:else}
					Registrar item
				{/if}
			</button>
		</div>
	</form>
{/if}
