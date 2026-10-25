<script lang="ts">
	import Footer from '#lib/components/layout/Footer.svelte';
	import NavHeader from '#lib/components/layout/NavHeader.svelte';
	import type { LayoutProps } from './$types';

	let { children }: LayoutProps = $props();
</script>

<div class="flex min-h-screen flex-col bg-white">
	<NavHeader />
	<main class="flex-1">
		{@render children()}
	</main>
	<Footer />
</div>
