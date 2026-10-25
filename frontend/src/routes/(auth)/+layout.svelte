<script lang="ts">
	import NavHeader from '#lib/components/layout/NavHeader.svelte';
	import type { LayoutProps } from './$types';

	let { children }: LayoutProps = $props();
</script>

<svelte:head>
	<meta
		name="description"
		content="JapanToGo - Compra assistida e redirecionamento de encomendas do Japão para o Brasil. Do seu purchase ao seu doorstep."
	/>
</svelte:head>

<div class="flex min-h-screen flex-col bg-slate-50">
	<NavHeader />
	<main class="flex flex-1 items-center justify-center px-4 py-12">
		<div class="w-full max-w-md">
			{@render children()}
		</div>
	</main>
</div>
