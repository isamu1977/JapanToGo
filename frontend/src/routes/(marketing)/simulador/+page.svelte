<script lang="ts">
	import LandedCostCalculator from '#lib/components/ui/LandedCostCalculator.svelte';
</script>

<svelte:head>
	<title>Simulador de custo de importação - JapanToGo</title>
	<meta
		name="description"
		content="Simule o custo total de importação (landed cost) de compras no Japão: conversão JPY/BRL, taxa de 20% com piso de ¥ 2.000, frete estimado e impostos brasileiros RTS + ICMS."
	/>
</svelte:head>

<section class="border-b border-slate-200 bg-slate-50 py-14">
	<div class="mx-auto max-w-4xl px-4">
		<p class="text-xs font-semibold tracking-widest text-brand-600 uppercase">
			Landed cost calculator
		</p>
		<h1 class="mt-3 text-3xl font-bold text-ink-900 sm:text-4xl">
			Simulador de custo de importação
		</h1>
		<p class="mt-4 text-slate-600">
			Descubra quanto vai custar realmente receber o seu pedido no Brasil. O simulador considera a
			taxa de serviço da JapanToGo, a estimativa de frete internacional por faixa de peso e a
			projeção dos impostos brasileiros (RTS 60% + ICMS calculado por dentro).
		</p>
	</div>
</section>

<section class="mx-auto max-w-4xl px-4 py-12">
	<LandedCostCalculator />

	<div class="mt-10 grid gap-5 sm:grid-cols-3">
		<div class="card p-5">
			<h2 class="text-sm font-semibold text-ink-900">Taxa de serviço</h2>
			<p class="mt-2 text-sm leading-relaxed text-slate-600">
				20% sobre o valor dos itens (na compra assistida) ou valor declarado (no redirecionamento
				puro), com piso de ¥ 2.000 para pedidos abaixo de ¥ 10.000.
			</p>
		</div>
		<div class="card p-5">
			<h2 class="text-sm font-semibold text-ink-900">Frete internacional</h2>
			<p class="mt-2 text-sm leading-relaxed text-slate-600">
				Estimativa por faixa de 500 g. EMS para envios rápidos e Small Packet (até 2 kg) para a
				opção econômica.
			</p>
		</div>
		<div class="card p-5">
			<h2 class="text-sm font-semibold text-ink-900">Impostos no Brasil</h2>
			<p class="mt-2 text-sm leading-relaxed text-slate-600">
				Projeção de 60% de RTS sobre o valor aduaneiro e ICMS de 18% aplicado sobre o valor
				aduaneiro acrescido do RTS (por dentro).
			</p>
		</div>
	</div>

	<p class="mt-8 rounded-2xl bg-amber-50 p-4 text-sm text-amber-900">
		A simulação usa uma cotação de referência com margem de segurança e não representa uma proposta
		comercial. O valor final pode variar conforme a cotação do dia, o regime tributário e a taxa
		aplicada pela transportadora.
	</p>
</section>
