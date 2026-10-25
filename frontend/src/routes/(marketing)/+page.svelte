<script lang="ts">
	import FaqAccordion from '#lib/components/landing/FaqAccordion.svelte';
	import FinalCta from '#lib/components/landing/FinalCta.svelte';
	import HeroSection from '#lib/components/landing/HeroSection.svelte';
	import OperationalPillars from '#lib/components/landing/OperationalPillars.svelte';
	import StoreShowcase from '#lib/components/landing/StoreShowcase.svelte';
	import WorkflowComparison from '#lib/components/landing/WorkflowComparison.svelte';
</script>

<svelte:head>
	<title>JapanToGo - FROM JAPAN TO YOUR DOOR</title>
	<meta
		name="description"
		content="Compra assistida e redirecionamento de encomendas do Japão para o Brasil, com galpão próprio, pesagem, inspeção fotográfica e simulação de custo de importação."
	/>
</svelte:head>

<HeroSection />

<WorkflowComparison />

<StoreShowcase />

<OperationalPillars />

<FaqAccordion />

<FinalCta />
