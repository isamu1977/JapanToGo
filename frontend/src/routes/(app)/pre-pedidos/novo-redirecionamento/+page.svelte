<script lang="ts">
	import { goto } from '$app/navigation';
	import { CircleAlert, FileText, LoaderCircle, Upload } from 'lucide-svelte';
	import { api } from '#lib/api/client';
	import type { PreOrder } from '#lib/api/types';

	let storeName = $state('');
	let description = $state('');
	let expectedTracking = $state('');
	let notes = $state('');
	let receipt = $state<File | null>(null);
	let submitting = $state(false);
	let failure = $state<string | null>(null);

	async function handleSubmit(event: SubmitEvent) {
		if (!receipt) {
			failure = 'O comprovante de compra é obrigatório.';
			event.preventDefault();
			return;
		}

		failure = null;
		submitting = true;

		try {
			const body = new FormData();
			body.append('store_name', storeName.trim());
			body.append('description', description.trim());
			if (expectedTracking.trim())
				body.append('expected_domestic_tracking', expectedTracking.trim());
			if (notes.trim()) body.append('notes', notes.trim());
			body.append('receipt', receipt);

			await api.postForm<PreOrder>('/api/v1/pre-orders/forwarding', body);
			await goto('/pre-pedidos');
		} catch (error) {
			failure = error instanceof Error ? error.message : 'Não foi possível enviar o pedido.';
		} finally {
			submitting = false;
		}
	}

	function onFileChange(event: Event) {
		const input = event.currentTarget as HTMLInputElement;
		receipt = input.files?.[0] ?? null;
	}
</script>

<svelte:head>
	<title>Novo redirecionamento - JapanToGo</title>
</svelte:head>

<header class="mb-6">
	<h1 class="text-2xl font-bold text-ink-900">Novo redirecionamento</h1>
	<p class="mt-1 text-sm text-slate-600">
		Você já comprou no Japão? Informe o rastreio da loja e anexe o comprovante de compra para quebps
		o pacote seja identificado no check-in.
	</p>
</header>

<form class="grid gap-6 lg:grid-cols-3" onsubmit={handleSubmit}>
	<div class="space-y-4 lg:col-span-2">
		<label class="block">
			<span class="label">Nome da loja</span>
			<input
				type="text"
				required
				bind:value={storeName}
				class="input mt-1"
				placeholder="Amazon JP, Rakuten, Mercari..."
			/>
		</label>

		<label class="block">
			<span class="label">Descrição do pedido</span>
			<input
				type="text"
				required
				bind:value={description}
				class="input mt-1"
				placeholder="Caixa de sapatos Nike, tamanho 42"
			/>
		</label>

		<label class="block">
			<span class="label">Rastreio doméstico esperado (opcional)</span>
			<input
				type="text"
				bind:value={expectedTracking}
				class="input mt-1"
				placeholder="123456789012"
			/>
		</label>

		<label class="block">
			<span class="label">Observações (opcional)</span>
			<textarea
				rows="3"
				bind:value={notes}
				class="input mt-1"
				placeholder="Ex.: a caixa veio com a nota fiscal dentro"></textarea>
		</label>

		<div>
			<span class="label">Comprovante de compra (obrigatório)</span>
			<label
				class="mt-1 flex cursor-pointer flex-col items-center justify-center gap-2 rounded-xl border-2 border-dashed border-slate-300 bg-slate-50 px-4 py-8 text-center transition hover:border-brand-300 hover:bg-brand-50/40"
			>
				<input
					type="file"
					accept="image/png,image/jpeg,image/webp,application/pdf"
					required
					class="sr-only"
					onchange={onFileChange}
				/>
				{#if receipt}
					<FileText size={28} class="text-brand-600" />
					<span class="text-sm font-medium text-ink-900">{receipt.name}</span>
					<span class="text-xs text-slate-500">
						{(receipt.size / 1024).toFixed(0)} KB · clique para trocar
					</span>
				{:else}
					<Upload size={28} class="text-slate-400" />
					<span class="text-sm font-medium text-ink-900">Clique para enviar o comprovante</span>
					<span class="text-xs text-slate-500">JPG, PNG, WebP ou PDF · até 5 MB</span>
				{/if}
			</label>
		</div>
	</div>

	<aside class="lg:sticky lg:top-6 lg:self-start">
		<div class="card p-5">
			<h2 class="text-base font-semibold text-ink-900">Como funciona</h2>
			<ol class="mt-4 space-y-3 text-sm text-slate-600">
				<li class="flex gap-3">
					<span
						class="flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-slate-100 text-xs font-semibold"
						>1</span
					>
					O pacote chega no nosso galpão com o código do seu Box.
				</li>
				<li class="flex gap-3">
					<span
						class="flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-slate-100 text-xs font-semibold"
						>2</span
					>
					A equipe pesa o item e registra até 5 fotos de inspeção.
				</li>
				<li class="flex gap-3">
					<span
						class="flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-slate-100 text-xs font-semibold"
						>3</span
					>
					Você confere em “Meus Pacotes” e solicita o envio ao Brasil.
				</li>
			</ol>

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
					Enviar redirecionamento
				{/if}
			</button>
		</div>
	</aside>
</form>
