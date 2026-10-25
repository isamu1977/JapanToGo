<script lang="ts">
	import '../routes/layout.css';
	import { registerServiceWorker } from '#lib/pwa';
	import CookieBanner from '#lib/components/ui/CookieBanner.svelte';
	import { initCookieConsent } from '#lib/stores/cookies';

	import type { LayoutProps } from './$types';

	let { children }: LayoutProps = $props();

	$effect(() => {
		registerServiceWorker();
		initCookieConsent();
	});
</script>

<svelte:head>
	<meta name="theme-color" content="#e11d48" />
	<link rel="manifest" href="/manifest.json" />
	<link rel="apple-touch-icon" href="/icons/apple-touch-icon.png" />
	<link rel="icon" type="image/png" sizes="48x48" href="/icons/favicon-48.png" />
	<meta name="mobile-web-app-capable" content="yes" />
	<meta name="apple-mobile-web-app-capable" content="yes" />
	<meta name="apple-mobile-web-app-status-bar-style" content="default" />
</svelte:head>

{@render children()}

<CookieBanner />
