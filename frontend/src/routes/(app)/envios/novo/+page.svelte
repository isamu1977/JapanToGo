<script lang="ts">
	import { goto } from '$app/navigation';
	import { CircleAlert, LoaderCircle, Plus, Trash2 } from 'lucide-svelte';
	import { api } from '#lib/api/client';
	import type { Shipment, ShippingMethod } from '#lib/api/types';
	import { formatWeight } from '#lib/utils/formatters';
	import { formatJPY } from '#lib/utils/currency';
	import type { PageProps } from './$types';

	interface CustomsLine {
		description: string;
		quantity: number;
		declared_value_jpy: number;
	}

	let { data }: PageProps = $props();

	let selected = $state<string[]>([]);
	let shippingMethod = $state<ShippingMethod>('ems');
	let customsLines = $state<CustomsLine[]>([
		{ description: '', quantity: 1, declared_value_jpy: 0 }
	]);

	let recipientName = $state('');
	let recipientCpf = $state('');
	let recipientPhone = $state('');
	let recipientPostalCode = $state('');
	let recipientAddress = $state('');
	let recipientState = $state('');
	let recipientCity = $state('');

	let submitting = $state(false);
	let failure = $state<string | null>(null);

	const selectedItems = $derived(data.items.filter((item) => selected.includes(item.id)));
	const totalWeight = $derived(selectedItems.reduce((sum, item) => sum + item.weight_grams, 0));
	const declaredTotal = $derived(
		customsLines.reduce((sum, line) => sum + (line.declared_value_jpy || 0), 0)
	);

	const cpfValid = $derived(/^\d{11}$/.test(recipientCpf.replace(/\D/g, '')));

	function toggleItem(id: string) {
		selected = selected.includes(id) ? selected.filter((value) => value !== id) : [...selected, id];
	}

	function addLine() {
		customsLines.push({ description: '', quantity: 1, declared_value_jpy: 0 });
	}

	function removeLine(index: number) {
		customsLines.splice(index, 1);
		if (customsLines.length === 0) addLine();
	}

	async function handleSubmit(event: SubmitEvent) {
		event.preventDefault();
		failure = null;

		if (selected.length === 0) {
			failure = 'Selecione ao menos um item do seu Box.';
			return;
		}
		if (!cpfValid) {
			failure = 'Informe um CPF válido com 11 dígitos.';
			return;
		}

		submitting = true;
		try {
			await api.post<Shipment>('/api/v1/shipments/request', {
				suite_item_ids: selected,
				shipping_method: shippingMethod,
				customs_declaration: {
					items: customsLines.map((line) => ({
						description: line.description.trim(),
						quantity: Number(line.quantity) || 1,
						declared_value_jpy: Number(line.declared_value_jpy) || 0
					}))
				},
				recipient_name: recipientName.trim(),
				recipient_cpf: recipientCpf.replace(/\D/g, ''),
				recipient_phone: recipientPhone.trim(),
				recipient_postal_code: recipientPostalCode.trim(),
				recipient_address: recipientAddress.trim(),
				recipient_state: recipientState.trim() || null,
				recipient_city: recipientCity.trim() || null
			});
			await goto('/envios');
		} catch (error) {
			failure = error instanceof Error ? error.message : 'Não foi possível criar o envio.';
		} finally {
			submitting = false;
		}
	}
</script>

<svelte:head>
	<title>Novo envio - JapanToGo</title>
</svelte:head>

<header class="mb-6">
	<h1 class="text-2xl font-bold text-ink-900">Novo envio internacional</h1>
	<p class="mt-1 text-sm text-slate-600">
		Selecione os itens do seu Box, preencha a declaração aduaneira e os dados do destinatário no
		Brasil.
	</p>
</header>

<form class="grid gap-6 lg:grid-cols-3" onsubmit={handleSubmit}>
	<div class="space-y-6 lg:col-span-2">
		<section class="card p-5">
			<h2 class="text-base font-semibold text-ink-900">1. Itens do seu Box</h2>
			{#if data.items.length === 0}
				<p class="mt-3 text-sm text-slate-500">
					Nenhum item disponível em estoque. Aguarde o check-in dos seus pacotes.
				</p>
			{:else}
				<ul class="mt-4 space-y-2">
					{#each data.items as item (item.id)}
						<li>
							<label
								class="flex cursor-pointer items-center gap-3 rounded-xl border p-3 transition {selected.includes(
									item.id
								)
									? 'border-brand-300 bg-brand-50'
									: 'border-slate-200 hover:bg-slate-50'}"
							>
								<input
									type="checkbox"
									checked={selected.includes(item.id)}
									onchange={() => toggleItem(item.id)}
									class="h-4 w-4"
								/>
								<span class="min-w-0 flex-1">
									<span class="block truncate text-sm font-medium text-ink-900">
										{item.description}
									</span>
									<span class="block text-xs text-slate-500">
										{formatWeight(item.weight_grams)}
									</span>
								</span>
							</label>
						</li>
					{/each}
				</ul>
				{#if selected.length > 0}
					<p class="mt-3 text-sm text-slate-600">
						{selected.length}
						{selected.length === 1 ? 'item selecionado' : 'itens selecionados'} ·{' '}
						<strong>{formatWeight(totalWeight)}</strong>
					</p>
				{/if}
			{/if}
		</section>

		<section class="card p-5">
			<h2 class="text-base font-semibold text-ink-900">2. Declaração aduaneira</h2>
			<p class="mt-1 text-sm text-slate-600">
				Descreva os itens em inglês, com quantidades e valores declarados em JPY.
			</p>

			<div class="mt-4 space-y-3">
				{#each customsLines as line, index (index)}
					<div class="rounded-xl border border-slate-200 p-3">
						<div class="grid gap-3 sm:grid-cols-12">
							<label class="block sm:col-span-6">
								<span class="label">Descrição (inglês)</span>
								<input
									type="text"
									required
									bind:value={line.description}
									class="input mt-1"
									placeholder="T-shirt"
								/>
							</label>
							<label class="block sm:col-span-2">
								<span class="label">Qtd.</span>
								<input
									type="number"
									required
									min="1"
									bind:value={line.quantity}
									class="input mt-1"
								/>
							</label>
							<label class="block sm:col-span-4">
								<span class="label">Valor declarado (¥)</span>
								<input
									type="number"
									required
									min="1"
									step="1"
									bind:value={line.declared_value_jpy}
									class="input mt-1"
								/>
							</label>
						</div>

						{#if customsLines.length > 1}
							<button
								type="button"
								onclick={() => removeLine(index)}
								class="mt-2 inline-flex items-center gap-1.5 text-xs font-medium text-red-600 hover:underline"
							>
								<Trash2 size={14} /> Remover linha
							</button>
						{/if}
					</div>
				{/each}
			</div>

			<button type="button" onclick={addLine} class="btn-secondary mt-3">
				<Plus size={15} /> Adicionar linha
			</button>
		</section>

		<section class="card p-5">
			<h2 class="text-base font-semibold text-ink-900">3. Destinatário no Brasil</h2>

			<div class="mt-4 grid gap-3 sm:grid-cols-2">
				<label class="block">
					<span class="label">Nome completo</span>
					<input type="text" required bind:value={recipientName} class="input mt-1" />
				</label>
				<label class="block">
					<span class="label">CPF</span>
					<input
						type="text"
						required
						inputmode="numeric"
						bind:value={recipientCpf}
						class="input mt-1 {recipientCpf && !cpfValid ? 'border-red-400' : ''}"
						placeholder="000.000.000-00"
					/>
					{#if recipientCpf && !cpfValid}
						<span class="mt-1 block text-xs text-red-600">CPF inválido.</span>
					{/if}
				</label>
				<label class="block">
					<span class="label">Telefone</span>
					<input type="tel" required bind:value={recipientPhone} class="input mt-1" />
				</label>
				<label class="block">
					<span class="label">CEP</span>
					<input
						type="text"
						required
						bind:value={recipientPostalCode}
						class="input mt-1"
						placeholder="01310-100"
					/>
				</label>
				<label class="block">
					<span class="label">Estado (UF)</span>
					<input type="text" bind:value={recipientState} class="input mt-1" placeholder="SP" />
				</label>
				<label class="block">
					<span class="label">Cidade</span>
					<input
						type="text"
						bind:value={recipientCity}
						class="input mt-1"
						placeholder="São Paulo"
					/>
				</label>
				<label class="block sm:col-span-2">
					<span class="label">Endereço completo</span>
					<textarea
						rows="2"
						required
						bind:value={recipientAddress}
						class="input mt-1"
						placeholder="Rua, número, complemento, bairro"></textarea>
				</label>
			</div>
		</section>
	</div>

	<aside class="lg:sticky lg:top-6 lg:self-start">
		<div class="card p-5">
			<h2 class="text-base font-semibold text-ink-900">Modalidade de envio</h2>

			<div class="mt-3 space-y-2">
				<label
					class="flex cursor-pointer items-start gap-3 rounded-xl border p-3 transition {shippingMethod ===
					'ems'
						? 'border-brand-300 bg-brand-50'
						: 'border-slate-200 hover:bg-slate-50'}"
				>
					<input type="radio" bind:group={shippingMethod} value="ems" class="mt-0.5 h-4 w-4" />
					<span>
						<span class="block text-sm font-medium text-ink-900">EMS</span>
						<span class="block text-xs text-slate-500">Expresso, rastreamento individual</span>
					</span>
				</label>
				<label
					class="flex cursor-pointer items-start gap-3 rounded-xl border p-3 transition {shippingMethod ===
					'small_packet'
						? 'border-brand-300 bg-brand-50'
						: 'border-slate-200 hover:bg-slate-50'}"
				>
					<input
						type="radio"
						bind:group={shippingMethod}
						value="small_packet"
						class="mt-0.5 h-4 w-4"
					/>
					<span>
						<span class="block text-sm font-medium text-ink-900">Small Packet</span>
						<span class="block text-xs text-slate-500">Econômico, até 2 kg</span>
					</span>
				</label>
			</div>

			<dl class="mt-4 space-y-2 border-t border-slate-100 pt-4 text-sm">
				<div class="flex justify-between">
					<dt class="text-slate-600">Itens</dt>
					<dd class="font-medium text-ink-900">{selected.length}</dd>
				</div>
				<div class="flex justify-between">
					<dt class="text-slate-600">Peso total</dt>
					<dd class="font-medium text-ink-900">{formatWeight(totalWeight)}</dd>
				</div>
				<div class="flex justify-between">
					<dt class="text-slate-600">Valor declarado</dt>
					<dd class="font-medium text-ink-900">{formatJPY(declaredTotal)}</dd>
				</div>
			</dl>

			{#if failure}
				<p
					class="mt-4 flex items-start gap-2 rounded-xl bg-red-50 px-3 py-2.5 text-sm text-red-700"
					role="alert"
				>
					<CircleAlert size={16} class="mt-0.5 shrink-0" />
					<span>{failure}</span>
				</p>
			{/if}

			<button type="submit" class="btn-primary mt-5 w-full" disabled={submitting}>
				{#if submitting}
					<LoaderCircle size={16} class="animate-spin" /> Enviando...
				{:else}
					Solicitar envio
				{/if}
			</button>

			<p class="mt-3 text-xs leading-relaxed text-slate-400">
				O frete final é calculado pela nossa operação e informado na etapa de despacho.
			</p>
		</div>
	</aside>
</form>
