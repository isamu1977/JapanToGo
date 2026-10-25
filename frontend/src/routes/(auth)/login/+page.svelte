<script lang="ts">
	import { goto } from '$app/navigation';
	import { CircleAlert, LoaderCircle } from 'lucide-svelte';
	import { error, loading, login } from '#lib/stores/auth';

	let email = $state('');
	let password = $state('');

	async function submit(event: SubmitEvent) {
		event.preventDefault();
		error.set(null);
		try {
			const profile = await login(email, password);
			await goto(profile.role === 'admin' ? '/admin/dashboard' : '/dashboard');
		} catch {
			// The error message is already exposed through the store.
		}
	}
</script>

<svelte:head>
	<title>Entrar - JapanToGo</title>
</svelte:head>

<div class="card p-6 sm:p-8">
	<h1 class="text-2xl font-bold text-ink-900">Entrar na sua conta</h1>
	<p class="mt-1.5 text-sm text-slate-600">Acesse seus pacotes, pré-pedidos e envios.</p>

	{#if $error}
		<p
			class="mt-5 flex items-start gap-2 rounded-xl bg-red-50 px-3 py-2.5 text-sm text-red-700"
			role="alert"
		>
			<CircleAlert size={16} class="mt-0.5 shrink-0" />
			<span>{$error}</span>
		</p>
	{/if}

	<form class="mt-6 space-y-4" onsubmit={submit}>
		<label class="block">
			<span class="label">E-mail</span>
			<input
				type="email"
				name="email"
				required
				autocomplete="email"
				bind:value={email}
				class="input mt-1"
				placeholder="voce@example.com"
			/>
		</label>

		<label class="block">
			<span class="label">Senha</span>
			<input
				type="password"
				name="password"
				required
				autocomplete="current-password"
				bind:value={password}
				class="input mt-1"
				placeholder="••••••••"
			/>
		</label>

		<button type="submit" class="btn-primary w-full" disabled={$loading}>
			{#if $loading}
				<LoaderCircle size={16} class="animate-spin" /> Entrando...
			{:else}
				Entrar
			{/if}
		</button>
	</form>

	<p class="mt-6 text-center text-sm text-slate-600">
		Ainda não tem conta?
		<a href="/register" class="font-medium text-brand-700 underline">Criar conta grátis</a>
	</p>
</div>
