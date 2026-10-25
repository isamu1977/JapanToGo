<script lang="ts">
	import { goto } from '$app/navigation';
	import { CircleAlert, LoaderCircle } from 'lucide-svelte';
	import { error, loading, register } from '#lib/stores/auth';

	let fullName = $state('');
	let email = $state('');
	let phone = $state('');
	let password = $state('');
	let confirmPassword = $state('');
	let acceptTerms = $state(false);
	let acceptPrivacy = $state(false);

	const passwordMismatch = $derived(confirmPassword.length > 0 && password !== confirmPassword);

	async function submit(event: SubmitEvent) {
		event.preventDefault();
		error.set(null);

		if (password !== confirmPassword) {
			error.set('As senhas não conferem.');
			return;
		}

		try {
			await register({
				email,
				password,
				full_name: fullName,
				phone,
				accept_terms: acceptTerms,
				accept_privacy: acceptPrivacy
			});
			await goto('/dashboard');
		} catch {
			// The error message is already exposed through the store.
		}
	}
</script>

<svelte:head>
	<title>Criar conta - JapanToGo</title>
</svelte:head>

<div class="card p-6 sm:p-8">
	<h1 class="text-2xl font-bold text-ink-900">Criar sua conta</h1>
	<p class="mt-1.5 text-sm text-slate-600">
		Você recebe um código único para o seu Box no Japão, pronto para usar nas lojas.
	</p>

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
			<span class="label">Nome completo</span>
			<input
				type="text"
				name="full_name"
				required
				minlength="2"
				autocomplete="name"
				bind:value={fullName}
				class="input mt-1"
				placeholder="Maria Silva"
			/>
		</label>

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
			<span class="label">Telefone</span>
			<input
				type="tel"
				name="phone"
				required
				minlength="6"
				autocomplete="tel"
				bind:value={phone}
				class="input mt-1"
				placeholder="+55 11 99999-0000"
			/>
		</label>

		<div class="grid gap-4 sm:grid-cols-2">
			<label class="block">
				<span class="label">Senha</span>
				<input
					type="password"
					name="password"
					required
					minlength="8"
					autocomplete="new-password"
					bind:value={password}
					class="input mt-1"
					placeholder="mínimo 8 caracteres"
				/>
			</label>

			<label class="block">
				<span class="label">Confirmar senha</span>
				<input
					type="password"
					name="confirm_password"
					required
					minlength="8"
					autocomplete="new-password"
					bind:value={confirmPassword}
					class="input mt-1 {passwordMismatch ? 'border-red-400' : ''}"
				/>
			</label>
		</div>

		{#if passwordMismatch}
			<p class="text-sm text-red-600">As senhas não conferem.</p>
		{/if}

		<fieldset class="space-y-2 rounded-xl bg-slate-50 p-4">
			<legend class="px-1 text-xs font-semibold tracking-wide text-slate-500 uppercase">
				Termos legais
			</legend>
			<label class="flex items-start gap-2 text-sm text-slate-700">
				<input type="checkbox" bind:checked={acceptTerms} class="mt-0.5" required />
				<span>
					Li e aceito os
					<a href="/termos" class="font-medium text-brand-700 underline">Termos de uso (利用規約)</a
					>.
				</span>
			</label>
			<label class="flex items-start gap-2 text-sm text-slate-700">
				<input type="checkbox" bind:checked={acceptPrivacy} class="mt-0.5" required />
				<span>
					Li e aceito a
					<a href="/privacidade" class="font-medium text-brand-700 underline"
						>Política de privacidade (プライバシーポリシー)</a
					>.
				</span>
			</label>
		</fieldset>

		<button type="submit" class="btn-primary w-full" disabled={$loading}>
			{#if $loading}
				<LoaderCircle size={16} class="animate-spin" /> Criando conta...
			{:else}
				Criar conta
			{/if}
		</button>
	</form>

	<p class="mt-6 text-center text-sm text-slate-600">
		Já tem conta?
		<a href="/login" class="font-medium text-brand-700 underline">Entrar</a>
	</p>
</div>
