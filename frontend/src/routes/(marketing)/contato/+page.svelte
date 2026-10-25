<script lang="ts">
	import { api, ApiError } from '#lib/api/client';
	import { suiteCode } from '#lib/stores/auth';

	let name = $state('');
	let email = $state('');
	let subject = $state('Dúvida sobre envio');
	let userSuite = $state('');
	let message = $state('');

	let isSubmitting = $state(false);
	let successMessage = $state<string | null>(null);
	let errorMessage = $state<string | null>(null);

	// Pre-fill suite code if customer is already logged in
	$effect(() => {
		if ($suiteCode && !userSuite) {
			userSuite = $suiteCode;
		}
	});

	async function handleSubmit(event: SubmitEvent) {
		event.preventDefault();
		isSubmitting = true;
		successMessage = null;
		errorMessage = null;

		try {
			const res = await api.post<{ success: boolean; message: string }>('/api/contact', {
				name: name.trim(),
				email: email.trim(),
				subject,
				suite_code: userSuite.trim() ? userSuite.trim() : null,
				message: message.trim()
			});

			successMessage = res.message;
			name = '';
			email = '';
			message = '';
		} catch (err) {
			if (err instanceof ApiError) {
				errorMessage = err.message;
			} else {
				errorMessage =
					'Não foi possível enviar a mensagem no momento. Tente novamente ou use nosso WhatsApp.';
			}
		} finally {
			isSubmitting = false;
		}
	}
</script>

<svelte:head>
	<title>Canais de Atendimento e Suporte - JapanToGo</title>
	<meta
		name="description"
		content="Fale com a equipe JapanToGo no Japão. Suporte a compras assistidas, consolidação de pacotes e dúvidas de envio internacional."
	/>
</svelte:head>

<!-- Header da página -->
<section class="border-b border-slate-200 bg-slate-50 py-12 lg:py-16">
	<div class="mx-auto max-w-5xl px-4 sm:px-6">
		<div class="flex items-center gap-2">
			<span class="inline-flex h-2.5 w-2.5 animate-pulse rounded-full bg-emerald-500"></span>
			<span class="text-xs font-semibold tracking-wider text-red-600 uppercase">
				Atendimento Oficial / お問い合わせ
			</span>
		</div>
		<h1 class="mt-3 text-3xl font-extrabold text-ink-900 sm:text-4xl">
			Como podemos ajudar sua importação?
		</h1>
		<p class="mt-2 text-base text-slate-600 sm:max-w-2xl">
			Nossa equipe operacional está baseada em Osaka, Japão, com atendimento bilíngue em português e
			japonês para compras assistidas, fotos de inspeção e desembaraço de envios.
		</p>
	</div>
</section>

<section class="py-12 lg:py-16">
	<div class="mx-auto max-w-5xl px-4 sm:px-6">
		<div class="grid gap-10 lg:grid-cols-12 lg:gap-12">
			<!-- Coluna Esquerda: Informações Oficiais e Horários (5 colunas) -->
			<div class="space-y-6 lg:col-span-5">
				<!-- Card WhatsApp -->
				<div
					class="overflow-hidden rounded-2xl border border-emerald-200 bg-gradient-to-br from-emerald-50/80 to-white p-6 shadow-sm"
				>
					<div class="flex items-start gap-4">
						<div
							class="flex h-12 w-12 shrink-0 items-center justify-center rounded-xl bg-emerald-500 text-white shadow-md shadow-emerald-500/20"
						>
							<svg class="h-6 w-6" fill="currentColor" viewBox="0 0 24 24">
								<path
									d="M.057 24l1.687-6.163c-1.041-1.804-1.588-3.849-1.587-5.946.003-6.556 5.338-11.891 11.893-11.891 3.181.001 6.167 1.24 8.413 3.488 2.245 2.248 3.481 5.236 3.48 8.414-.003 6.557-5.338 11.892-11.893 11.892-1.99-.001-3.951-.5-5.688-1.448l-6.305 1.654zm6.597-3.807c1.676.995 3.276 1.591 5.392 1.592 5.448 0 9.886-4.434 9.889-9.885.002-5.462-4.415-9.89-9.881-9.892-5.452 0-9.887 4.434-9.889 9.884-.001 2.225.651 3.891 1.746 5.634l-.999 3.648 3.742-.981zm11.387-5.464c-.074-.124-.272-.198-.57-.347-.297-.149-1.758-.868-2.031-.967-.272-.099-.47-.149-.669.149-.198.297-.768.967-.941 1.165-.173.198-.347.223-.644.074-.297-.149-1.255-.462-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.297-.347.446-.521.151-.172.2-.296.3-.495.099-.198.05-.372-.025-.521-.075-.148-.669-1.611-.916-2.206-.242-.579-.487-.501-.669-.51l-.57-.01c-.198 0-.52.074-.792.372s-1.04 1.016-1.04 2.479 1.065 2.876 1.213 3.074c.149.198 2.095 3.2 5.076 4.487.709.306 1.263.489 1.694.626.712.226 1.36.194 1.872.118.571-.085 1.758-.719 2.006-1.413.248-.695.248-1.29.173-1.414z"
								/>
							</svg>
						</div>
						<div>
							<h3 class="font-bold text-slate-900">WhatsApp de Atendimento</h3>
							<p class="mt-1 text-xs text-slate-600">
								Fale diretamente com nossa equipe para dúvidas rápidas, aprovação de orçamentos e
								rastreamento.
							</p>
							<a
								href="https://wa.me/818000000000?text=Ol%C3%A1%2C%20gostaria%20de%20tirar%20uma%20d%C3%BAvida%20sobre%20o%20JapanToGo"
								target="_blank"
								rel="noopener noreferrer"
								class="mt-3 inline-flex items-center gap-2 rounded-xl bg-emerald-600 px-4 py-2 text-xs font-bold text-white shadow transition-all hover:bg-emerald-500 active:scale-95"
							>
								<span>Iniciar conversa no WhatsApp</span>
								<svg class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
									<path
										stroke-linecap="round"
										stroke-linejoin="round"
										stroke-width="2"
										d="M14 5l7 7m0 0l-7 7m7-7H3"
									/>
								</svg>
							</a>
						</div>
					</div>
				</div>

				<!-- Card E-mail Oficial -->
				<div class="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
					<div class="flex items-start gap-4">
						<div
							class="flex h-11 w-11 shrink-0 items-center justify-center rounded-xl bg-slate-100 text-slate-700"
						>
							<svg class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
								<path
									stroke-linecap="round"
									stroke-linejoin="round"
									stroke-width="2"
									d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"
								/>
							</svg>
						</div>
						<div>
							<h3 class="font-semibold text-slate-900">E-mail Oficial</h3>
							<p class="mt-1 text-xs text-slate-500">
								Para notificações aduaneiras, orçamentos corporativos e auditoria de compras.
							</p>
							<p class="mt-2 text-sm font-semibold text-red-600">
								<a href="mailto:contato@japantogo.com" class="hover:underline">
									contato@japantogo.com
								</a>
							</p>
						</div>
					</div>
				</div>

				<!-- Card Horários Operacionais (Fusos JST e BRT) -->
				<div class="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
					<h3 class="flex items-center gap-2 text-sm font-bold text-slate-900">
						<svg
							class="h-4 w-4 text-slate-500"
							fill="none"
							viewBox="0 0 24 24"
							stroke="currentColor"
						>
							<path
								stroke-linecap="round"
								stroke-linejoin="round"
								stroke-width="2"
								d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"
							/>
						</svg>
						<span>Horário de Funcionamento Operacional</span>
					</h3>

					<div class="mt-4 space-y-3 text-xs">
						<div
							class="flex items-center justify-between rounded-xl border border-slate-100 bg-slate-50 p-3"
						>
							<span class="font-medium text-slate-700">🇯🇵 Japão (JST - Horário de Osaka):</span>
							<span class="font-bold text-ink-900">09:00 às 18:00 (Seg a Sex)</span>
						</div>
						<div
							class="flex items-center justify-between rounded-xl border border-slate-100 bg-slate-50 p-3"
						>
							<span class="font-medium text-slate-700">🇧🇷 Brasil (BRT - Horário de Brasília):</span>
							<span class="font-bold text-ink-900">21:00 às 06:00 (Seg a Sex)</span>
						</div>
					</div>
					<p class="mt-3 text-[11px] leading-relaxed text-slate-400">
						* Mensagens recebidas fora do horário comercial são respondidas no início do próximo
						turno de triagem no galpão de Osaka.
					</p>
				</div>
			</div>

			<!-- Coluna Direita: Formulário de Contato (7 colunas) -->
			<div class="lg:col-span-7">
				<div class="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm sm:p-8">
					<h2 class="text-xl font-bold text-ink-900">Envie uma mensagem</h2>
					<p class="mt-1 text-xs text-slate-500">
						Preencha o formulário abaixo. Nossa equipe retornará no seu e-mail cadastrado.
					</p>

					{#if successMessage}
						<div
							class="my-6 rounded-xl border border-emerald-200 bg-emerald-50 p-4 text-xs text-emerald-800"
							role="alert"
						>
							<div class="flex items-start gap-3">
								<svg
									class="mt-0.5 h-5 w-5 shrink-0 text-emerald-600"
									fill="none"
									viewBox="0 0 24 24"
									stroke="currentColor"
								>
									<path
										stroke-linecap="round"
										stroke-linejoin="round"
										stroke-width="2"
										d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
									/>
								</svg>
								<div>
									<p class="font-bold">Mensagem Enviada!</p>
									<p class="mt-1">{successMessage}</p>
								</div>
							</div>
						</div>
					{/if}

					{#if errorMessage}
						<div
							class="my-6 rounded-xl border border-red-200 bg-red-50 p-4 text-xs text-red-800"
							role="alert"
						>
							<p class="font-bold">Atenção</p>
							<p class="mt-1">{errorMessage}</p>
						</div>
					{/if}

					<form onsubmit={handleSubmit} class="mt-6 space-y-4">
						<div class="grid gap-4 sm:grid-cols-2">
							<div>
								<label for="contact-name" class="block text-xs font-semibold text-slate-700">
									Seu Nome Completo *
								</label>
								<input
									id="contact-name"
									type="text"
									required
									bind:value={name}
									placeholder="Ex: Rafael Takahashi"
									class="mt-1.5 w-full rounded-xl border border-slate-300 bg-white px-3.5 py-2.5 text-sm text-slate-900 shadow-sm transition-colors focus:border-red-600 focus:ring-1 focus:ring-red-600 focus:outline-none"
								/>
							</div>

							<div>
								<label for="contact-email" class="block text-xs font-semibold text-slate-700">
									Seu E-mail *
								</label>
								<input
									id="contact-email"
									type="email"
									required
									bind:value={email}
									placeholder="seu.email@exemplo.com"
									class="mt-1.5 w-full rounded-xl border border-slate-300 bg-white px-3.5 py-2.5 text-sm text-slate-900 shadow-sm transition-colors focus:border-red-600 focus:ring-1 focus:ring-red-600 focus:outline-none"
								/>
							</div>
						</div>

						<div class="grid gap-4 sm:grid-cols-2">
							<div>
								<label for="contact-subject" class="block text-xs font-semibold text-slate-700">
									Assunto *
								</label>
								<select
									id="contact-subject"
									bind:value={subject}
									class="mt-1.5 w-full rounded-xl border border-slate-300 bg-white px-3.5 py-2.5 text-sm text-slate-900 shadow-sm transition-colors focus:border-red-600 focus:ring-1 focus:ring-red-600 focus:outline-none"
								>
									<option value="Dúvida sobre envio">Dúvida sobre envio internacional</option>
									<option value="Orçamento de compra assistida">
										Orçamento de compra assistida
									</option>
									<option value="Suporte a pedido existente">
										Suporte a pedido existente no seu Box
									</option>
									<option value="Dúvidas sobre leilões (Yahoo/Mercari)">
										Dúvidas sobre leilões e usados
									</option>
									<option value="Outros">Outro assunto</option>
								</select>
							</div>

							<div>
								<label for="contact-suite" class="block text-xs font-semibold text-slate-700">
									Código do Box (opcional)
								</label>
								<input
									id="contact-suite"
									type="text"
									bind:value={userSuite}
									placeholder="Ex: JTG-8821"
									class="mt-1.5 w-full rounded-xl border border-slate-300 bg-white px-3.5 py-2.5 text-sm text-slate-900 shadow-sm transition-colors focus:border-red-600 focus:ring-1 focus:ring-red-600 focus:outline-none"
								/>
							</div>
						</div>

						<div>
							<label for="contact-message" class="block text-xs font-semibold text-slate-700">
								Mensagem * (mínimo 10 caracteres)
							</label>
							<textarea
								id="contact-message"
								required
								rows="5"
								bind:value={message}
								placeholder="Descreva detalhadamente sua dúvida, links dos produtos ou número do pacote..."
								class="mt-1.5 w-full rounded-xl border border-slate-300 bg-white px-3.5 py-2.5 text-sm text-slate-900 shadow-sm transition-colors focus:border-red-600 focus:ring-1 focus:ring-red-600 focus:outline-none"
							></textarea>
						</div>

						<div class="pt-2">
							<button
								type="submit"
								disabled={isSubmitting}
								class="inline-flex w-full items-center justify-center rounded-xl bg-red-600 px-6 py-3 text-sm font-bold text-white shadow-md shadow-red-950/20 transition-all hover:bg-red-500 disabled:opacity-50 sm:w-auto"
							>
								{#if isSubmitting}
									<span
										class="mr-2 inline-block h-4 w-4 animate-spin rounded-full border-2 border-white border-t-transparent"
									></span>
									<span>Enviando mensagem...</span>
								{:else}
									<span>Enviar Mensagem</span>
								{/if}
							</button>
						</div>
					</form>
				</div>
			</div>
		</div>
	</div>
</section>
