<script lang="ts">
	import { ExternalLink, HelpCircle, Store } from 'lucide-svelte';
	import AddressCard from '#lib/components/ui/AddressCard.svelte';
	import type { PageProps } from './$types';

	let { data }: PageProps = $props();

	const shops = [
		{
			name: 'Mercari (メルカリ)',
			format: 'Formato Japonês',
			hint: 'Cole o CEP 〒540-0027, selecione 大阪府 e coloque o código do seu Box em 建物名・部屋番号'
		},
		{
			name: 'Amazon Japan (Amazon.co.jp)',
			format: 'Romano ou Japonês',
			hint: 'Aceita caracteres em inglês. Preencha Address Line 2 com o nome do prédio e o código do seu Box'
		},
		{
			name: 'Rakuten (楽天市場)',
			format: 'Formato Japonês',
			hint: 'Cadastre no seu perfil Rakuten incluindo o código do seu Box no campo de complemento'
		},
		{
			name: 'Yahoo! Leilões (ヤフオク!)',
			format: 'Formato Japonês',
			hint: 'Preencha o campo その他 / 建物名 com o nome do prédio e o código do seu Box'
		},
		{
			name: 'AmiAmi & Surugaya',
			format: 'Formato Japonês',
			hint: 'Informe o endereço exatamente como mostrado na aba japonesa para entrega local'
		}
	];
</script>

<svelte:head>
	<title>Meu Endereço no Japão - JapanToGo</title>
</svelte:head>

<div class="space-y-8">
	<!-- Page Header -->
	<header>
		<p class="eyebrow text-brand-600">Galpão em Osaka</p>
		<h1 class="mt-1 text-2xl font-extrabold text-ink-900 sm:text-3xl">Meu Endereço no Japão</h1>
		<p class="mt-2 text-sm leading-relaxed text-slate-600 sm:text-base">
			Este é o endereço seguro do galpão da JapanToGo no Japão com o seu Box individual vinculado.
			Utilize-o como destinatário de entrega em qualquer marketplace ou loja japonesa.
		</p>
	</header>

	<!-- Address Card with Tabs and One-click copy -->
	<AddressCard address={data.address} />

	<!-- Shop Guide Section -->
	<section class="rounded-2xl border border-slate-200/80 bg-white p-5 shadow-xs sm:p-6">
		<div class="flex items-center gap-2.5 border-b border-slate-100 pb-3">
			<Store size={19} class="text-brand-600" />
			<h2 class="text-base font-bold text-ink-900">Dicas de Preenchimento nas Principais Lojas</h2>
		</div>

		<div class="mt-4 grid gap-3 sm:grid-cols-2">
			{#each shops as shop (shop.name)}
				<div
					class="rounded-xl border border-slate-100 bg-slate-50/70 p-3.5 transition hover:bg-slate-50"
				>
					<div class="flex items-center justify-between gap-2">
						<span class="text-sm font-bold text-ink-900">{shop.name}</span>
						<span
							class="rounded-md border border-slate-200 bg-white px-2 py-0.5 text-[11px] font-semibold text-slate-600"
						>
							{shop.format}
						</span>
					</div>
					<p class="mt-1.5 text-xs leading-relaxed text-slate-600">{shop.hint}</p>
				</div>
			{/each}
		</div>
	</section>
</div>
