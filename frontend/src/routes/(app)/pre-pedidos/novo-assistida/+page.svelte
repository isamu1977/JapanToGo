<script lang="ts">
	import { goto } from '$app/navigation';
	import { CircleAlert, LoaderCircle, Plus, Trash2 } from 'lucide-svelte';
	import { api } from '#lib/api/client';
	import type { PreOrder } from '#lib/api/types';
	import { formatJPY } from '#lib/utils/currency';

	interface Item {
		product_url: string;
		product_name: string;
		quantity: number;
		unit_price_jpy: number;
		options_description: string;
	}

	let items = $state<Item[]>([
		{ product_url: '', product_name: '', quantity: 1, unit_price_jpy: 0, options_description: '' }
	]);
	let notes = $state('');
	let submitting = $state(false);
	let failure = $state<string | null>(null);

	/** Mirror of the backend rule: 20% with a ¥ 2.000 floor below ¥ 10.000. */
	const itemsTotal = $derived(
		items.reduce((sum, item) => sum + item.quantity * (item.unit_price_jpy || 0), 0)
	);
	const proportionalFee = $derived(itemsTotal * 0.2);
	const fee = $derived(itemsTotal < 10000 ? Math.max(proportionalFee, 2000) : proportionalFee);
	const total = $derived(itemsTotal + fee);
	const floorApplied = $derived(itemsTotal > 0 && itemsTotal < 10000 && proportionalFee < 2000);

	function addItem() {
		items.push({
			product_url: '',
			product_name: '',
			quantity: 1,
			unit_price_jpy: 0,
			options_description: ''
		});
	}

	function removeItem(index: number) {
		items.splice(index, 1);
		if (items.length === 0) addItem();
	}

	async function submit(event: SubmitEvent) {
		event.preventDefault();
		failure = null;
		submitting = true;

		try {
			await api.post<PreOrder>('/api/v1/pre-orders/assisted', {
				items: items.map((item) => ({
					product_url: item.product_url.trim(),
					product_name: item.product_name.trim(),
					quantity: Number(item.quantity) || 1,
					unit_price_jpy: Number(item.unit_price_jpy) || 0,
					options_description: item.options_description.trim() || null
				})),
				notes: notes.trim() || null
			});
			await goto('/pre-pedidos');
		} catch (error) {
			failure = error instanceof Error ? error.message : 'Não foi possível enviar o pedido.';
		} finally {
			submitting = false;
		}
	}
</script>

<svelte:head>
	<title>Nova compra assistida - JapanToGo</title>
</svelte:head>

<header class="mb-6">
	<h1 class="text-2xl font-bold text-ink-900">Nova compra assistida</h1>
	<p class="mt-1 text-sm text-slate-600">
		Envie os links dos produtos que deseja comprar no Japão. A taxa de serviço é de 20% com piso de
		¥ 2.000.
	</p>
</header>

<form class="grid gap-6 lg:grid-cols-3" onsubmit={submit}>
	<div class="space-y-4 lg:col-span-2">
		{#each items as item, index (index)}
			<fieldset class="card p-5">
				<legend class="px-1 text-sm font-semibold text-ink-900">Item {index + 1}</legend>

				<div class="space-y-3">
					<label class="block">
						<span class="label">Link do produto</span>
						<input
							type="url"
							required
							placeholder="https://www.amazon.co.jp/dp/..."
							bind:value={item.product_url}
							class="input mt-1"
						/>
					</label>

					<label class="block">
						<span class="label">Nome do produto</span>
						<input
							type="text"
							required
							placeholder="Camiseta Uniqlo"
							bind:value={item.product_name}
							class="input mt-1"
						/>
					</label>

					<div class="grid gap-3 sm:grid-cols-2">
						<label class="block">
							<span class="label">Quantidade</span>
							<input
								type="number"
								required
								min="1"
								step="1"
								bind:value={item.quantity}
								class="input mt-1"
							/>
						</label>

						<label class="block">
							<span class="label">Preço unitário (¥)</span>
							<input
								type="number"
								required
								min="1"
								step="1"
								bind:value={item.unit_price_jpy}
								class="input mt-1"
							/>
						</label>
					</div>

					<label class="block">
						<span class="label">Especificações (tamanho, cor, observações)</span>
						<input
							type="text"
							placeholder="Tamanho M, cor preta"
							bind:value={item.options_description}
							class="input mt-1"
						/>
					</label>
				</div>

				{#if items.length > 1}
					<button
						type="button"
						onclick={() => removeItem(index)}
						class="mt-4 inline-flex items-center gap-1.5 text-sm font-medium text-red-600 hover:underline"
					>
						<Trash2 size={15} /> Remover item
					</button>
				{/if}
			</fieldset>
		{/each}

		<button type="button" onclick={addItem} class="btn-secondary">
			<Plus size={16} /> Adicionar outro item
		</button>

		<label class="block">
			<span class="label">Observações gerais (opcional)</span>
			<textarea
				rows="3"
				bind:value={notes}
				class="input mt-1"
				placeholder="Ex.: enviar em uma única caixa, presente de aniversário..."></textarea>
		</label>
	</div>

	<aside class="lg:sticky lg:top-6 lg:self-start">
		<div class="card p-5">
			<h2 class="text-base font-semibold text-ink-900">Prévia do valor</h2>

			<dl class="mt-4 space-y-2 text-sm">
				<div class="flex justify-between">
					<dt class="text-slate-600">Total dos itens</dt>
					<dd class="font-medium text-ink-900">{formatJPY(itemsTotal)}</dd>
				</div>
				<div class="flex justify-between">
					<dt class="text-slate-600">Taxa de serviço (20%)</dt>
					<dd class="font-medium text-ink-900">{formatJPY(fee)}</dd>
				</div>
				<div class="flex justify-between border-t border-slate-200 pt-2">
					<dt class="font-semibold text-ink-900">Total</dt>
					<dd class="text-lg font-bold text-brand-700">{formatJPY(total)}</dd>
				</div>
			</dl>

			{#if floorApplied}
				<p class="mt-3 rounded-xl bg-amber-50 px-3 py-2 text-xs text-amber-800">
					A taxa mínima de ¥ 2.000 foi aplicada porque o total dos itens é menor que ¥ 10.000.
				</p>
			{/if}

			{#if failure}
				<p
					class="mt-4 flex items-start gap-2 rounded-xl bg-red-50 px-3 py-2.5 text-sm text-red-700"
					role="alert"
				>
					<CircleAlert size={16} class="mt-0.5 shrink-0" />
					<span>{failure}</span>
				</p>
			{/if}

			<button
				type="submit"
				class="btn-primary mt-5 w-full"
				disabled={submitting || itemsTotal <= 0}
			>
				{#if submitting}
					<LoaderCircle size={16} class="animate-spin" /> Enviando...
				{:else}
					Enviar pré-pedido
				{/if}
			</button>

			<p class="mt-3 text-xs leading-relaxed text-slate-400">
				O frete internacional e os impostos brasileiros são cobrados na etapa de envio e não estão
				incluídos neste valor.
			</p>
		</div>
	</aside>
</form>
