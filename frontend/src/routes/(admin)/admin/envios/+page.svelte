<script lang="ts">
	import { CircleAlert, Copy, Download, LoaderCircle, Truck } from 'lucide-svelte';
	import { invalidateAll } from '$app/navigation';
	import { api } from '#lib/api/client';
	import type { JapanPostExport, Shipment } from '#lib/api/types';
	import { formatJPY } from '#lib/utils/currency';
	import {
		SHIPPING_METHOD_LABELS,
		SHIPMENT_STATUS_LABELS,
		formatDate,
		formatWeight,
		maskCpf
	} from '#lib/utils/formatters';
	import type { PageProps } from './$types';

	let { data }: PageProps = $props();

	let selected = $state<Shipment | null>(null);
	let totalWeight = $state<number | null>(null);
	let shippingFee = $state<number | null>(null);
	let trackingCode = $state('');
	let adminNotes = $state('');
	let saving = $state(false);
	let failure = $state<string | null>(null);

	let exportPayload = $state<JapanPostExport | null>(null);
	let exportText = $state('');
	let exportCsv = $state('');
	let exporting = $state(false);
	let copied = $state(false);

	const toneClasses: Record<string, string> = {
		green: 'bg-emerald-50 text-emerald-700',
		amber: 'bg-amber-50 text-amber-700',
		blue: 'bg-blue-50 text-blue-700',
		red: 'bg-red-50 text-red-700',
		gray: 'bg-slate-100 text-slate-600'
	};

	function toneOf(status: string): string {
		if (status === 'delivered') return 'green';
		if (status === 'requested') return 'amber';
		if (status === 'packed' || status === 'paid' || status === 'dispatched') return 'blue';
		return 'gray';
	}

	function openShipment(shipment: Shipment) {
		selected = shipment;
		totalWeight = shipment.total_weight_grams || null;
		shippingFee = shipment.shipping_fee_jpy || null;
		trackingCode = shipment.international_tracking_code ?? '';
		adminNotes = '';
		failure = null;
		exportPayload = null;
		exportText = '';
		exportCsv = '';
	}

	function closeShipment() {
		selected = null;
		failure = null;
	}

	async function dispatch() {
		if (!selected) return;
		saving = true;
		failure = null;

		try {
			const updated = await api.put<Shipment>(`/api/v1/admin/shipments/${selected.id}/dispatch`, {
				status: 'dispatched',
				total_weight_grams: totalWeight ?? undefined,
				shipping_fee_jpy: shippingFee ?? 0,
				international_tracking_code: trackingCode.trim() || null,
				admin_notes: adminNotes.trim() || null
			});
			data.shipments = data.shipments.map((shipment) =>
				shipment.id === updated.id ? updated : shipment
			);
			closeShipment();
			await invalidateAll();
		} catch (error) {
			failure = error instanceof Error ? error.message : 'Não foi possível despachar.';
		} finally {
			saving = false;
		}
	}

	async function exportForJapanPost() {
		if (!selected) return;
		exporting = true;
		failure = null;
		try {
			const response = await api.get<{
				payload: JapanPostExport;
				text: string;
				csv: string;
			}>(`/api/v1/admin/shipments/${selected.id}/export-japan-post`);
			exportPayload = response.payload;
			exportText = response.text;
			exportCsv = response.csv;
		} catch (error) {
			failure = error instanceof Error ? error.message : 'Não foi possível gerar a exportação.';
		} finally {
			exporting = false;
		}
	}

	async function copyExport() {
		try {
			await navigator.clipboard.writeText(exportText);
			copied = true;
			setTimeout(() => (copied = false), 1800);
		} catch {
			failure = 'Não foi possível copiar. Selecione o texto manualmente.';
		}
	}

	function downloadCsv() {
		const blob = new Blob([exportCsv], { type: 'text/csv;charset=utf-8' });
		const url = URL.createObjectURL(blob);
		const link = document.createElement('a');
		link.href = url;
		link.download = `japantogo-${selected?.id ?? 'shipment'}.csv`;
		link.click();
		URL.revokeObjectURL(url);
	}
</script>

<svelte:head>
	<title>Despacho - Operação JapanToGo</title>
</svelte:head>

<header class="mb-6">
	<h1 class="text-2xl font-bold text-ink-900">Despacho internacional</h1>
	<p class="mt-1 text-sm text-slate-600">
		Confirme o peso final, registre o rastreio e exporte os dados para o Japan Post.
	</p>
</header>

{#if data.shipments.length === 0}
	<div class="card p-10 text-center">
		<Truck size={32} class="mx-auto text-slate-300" />
		<p class="mt-4 text-sm text-slate-600">Nenhum envio na fila.</p>
	</div>
{:else}
	<ul class="space-y-3">
		{#each data.shipments as shipment (shipment.id)}
			<li class="card p-5">
				<div class="flex flex-wrap items-start justify-between gap-3">
					<div class="min-w-0">
						<div class="flex flex-wrap items-center gap-2">
							<span class="badge {toneClasses[toneOf(shipment.status)]}">
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

					<div class="flex flex-wrap gap-2">
						<button type="button" onclick={() => openShipment(shipment)} class="btn-secondary">
							<Truck size={15} /> Despachar
						</button>
						<button
							type="button"
							onclick={() => {
								openShipment(shipment);
								exportForJapanPost();
							}}
							class="btn-secondary"
						>
							<Download size={15} /> Exportar para Japan Post
						</button>
					</div>
				</div>

				{#if shipment.customs_declaration && shipment.customs_declaration.items.length > 0}
					<ul class="mt-3 space-y-0.5 border-t border-slate-100 pt-3 text-xs text-slate-500">
						{#each shipment.customs_declaration.items as line (line.description)}
							<li>
								· {line.description} × {line.quantity} — {formatJPY(line.declared_value_jpy)}
							</li>
						{/each}
					</ul>
				{/if}
			</li>
		{/each}
	</ul>
{/if}

{#if selected}
	<div
		class="fixed inset-0 z-50 overflow-y-auto bg-slate-900/60 p-4"
		role="dialog"
		aria-modal="true"
		aria-label="Despachar envio"
		tabindex="-1"
	>
		<div class="mx-auto my-8 w-full max-w-2xl space-y-4">
			<section class="rounded-2xl bg-white p-6 shadow-xl">
				<h2 class="text-lg font-semibold text-ink-900">Registrar despacho</h2>
				<p class="mt-1 text-sm text-slate-600">
					{selected.recipient_name} · {selected.recipient_address}
				</p>

				{#if failure}
					<p
						class="mt-4 flex items-start gap-2 rounded-xl bg-red-50 px-3 py-2.5 text-sm text-red-700"
					>
						<CircleAlert size={16} class="mt-0.5 shrink-0" />
						<span>{failure}</span>
					</p>
				{/if}

				<div class="mt-4 grid gap-3 sm:grid-cols-2">
					<label class="block">
						<span class="label">Peso final (gramas)</span>
						<input
							type="number"
							min="1"
							bind:value={totalWeight}
							class="input mt-1"
							placeholder="1450"
						/>
					</label>
					<label class="block">
						<span class="label">Frete final (¥)</span>
						<input
							type="number"
							min="0"
							step="1"
							bind:value={shippingFee}
							class="input mt-1"
							placeholder="3200"
						/>
					</label>
					<label class="block sm:col-span-2">
						<span class="label">Rastreio internacional</span>
						<input
							type="text"
							bind:value={trackingCode}
							class="input mt-1 font-mono"
							placeholder="EJ123456789JP"
						/>
					</label>
					<label class="block sm:col-span-2">
						<span class="label">Observações internas</span>
						<textarea rows="2" bind:value={adminNotes} class="input mt-1"></textarea>
					</label>
				</div>

				<div class="mt-6 flex justify-end gap-2">
					<button type="button" onclick={closeShipment} class="btn-secondary">Fechar</button>
					<button type="button" onclick={dispatch} class="btn-primary" disabled={saving}>
						{#if saving}
							<LoaderCircle size={16} class="animate-spin" /> Salvando...
						{:else}
							Confirmar despacho
						{/if}
					</button>
				</div>
			</section>

			{#if exportPayload}
				<section class="rounded-2xl bg-white p-6 shadow-xl">
					<div class="flex items-center justify-between gap-3">
						<h3 class="text-base font-semibold text-ink-900">Exportação para o Japan Post</h3>
						<div class="flex gap-2">
							<button type="button" onclick={copyExport} class="btn-secondary">
								<Copy size={15} />
								{copied ? 'Copiado!' : 'Copiar'}
							</button>
							<button type="button" onclick={downloadCsv} class="btn-secondary">
								<Download size={15} /> CSV
							</button>
						</div>
					</div>

					<pre
						class="mt-4 max-h-80 overflow-auto rounded-xl bg-slate-900 p-4 font-mono text-xs leading-relaxed text-slate-100">{exportText}</pre>

					<dl class="mt-4 grid gap-2 text-sm sm:grid-cols-2">
						<div class="flex justify-between">
							<dt class="text-slate-500">Destinatário</dt>
							<dd class="font-medium text-ink-900">{exportPayload.recipient_name}</dd>
						</div>
						<div class="flex justify-between">
							<dt class="text-slate-500">País</dt>
							<dd class="font-medium text-ink-900">{exportPayload.country_code}</dd>
						</div>
						<div class="flex justify-between">
							<dt class="text-slate-500">Valor declarado</dt>
							<dd class="font-medium text-ink-900">
								{formatJPY(exportPayload.total_declared_value_jpy)}
							</dd>
						</div>
						<div class="flex justify-between">
							<dt class="text-slate-500">Itens</dt>
							<dd class="font-medium text-ink-900">{exportPayload.total_quantity}</dd>
						</div>
					</dl>
				</section>
			{:else}
				<section class="rounded-2xl bg-white p-6 shadow-xl">
					<h3 class="text-base font-semibold text-ink-900">Exportação Japan Post</h3>
					<p class="mt-1 text-sm text-slate-600">
						Gere o payload no formato do sistema International Mail My Page para copiar e colar no
						portal da Japan Post.
					</p>
					<button
						type="button"
						onclick={exportForJapanPost}
						class="btn-primary mt-4"
						disabled={exporting}
					>
						{#if exporting}
							<LoaderCircle size={16} class="animate-spin" /> Gerando...
						{:else}
							<Download size={16} /> Exportar para Japan Post
						{/if}
					</button>
				</section>
			{/if}
		</div>
	</div>
{/if}
