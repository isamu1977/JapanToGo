<script lang="ts">
	import LegalPage from '#lib/components/layout/LegalPage.svelte';
	import { openCookiePreferences } from '#lib/stores/cookies';
</script>

<LegalPage
	title="Política de Cookies"
	titleJa="クッキーポリシー (Cookie Policy)"
	updated="25/10/2026"
>
	<p class="leading-relaxed">
		A <strong>JapanToGo Co., Ltd.</strong> utiliza cookies e tecnologias similares para garantir a
		segurança das operações do seu Box no Japão, autenticar transações e personalizar sua
		experiência de importação. Esta política explica de forma clara e transparente quais cookies são
		utilizados, suas finalidades e como você pode gerenciá-los a qualquer momento, em conformidade
		com a <strong>LGPD (Brasil - Lei 13.709/2018)</strong>, o <strong>GDPR (União Europeia)</strong>
		e a{' '}
		<strong>APPI (Japão - 個人情報保護法)</strong>.
	</p>
	<p class="mt-2 text-slate-500" lang="ja">
		JapanToGo 株式会社は、お客様の安全なセッション維持および利便性向上のために Cookie
		を使用しています。本ポリシーでは、使用する Cookie の種類、目的、および管理方法を説明します。
	</p>

	<!-- Botão interativo para alterar preferências -->
	<div class="my-6 rounded-2xl border border-amber-200 bg-amber-50/70 p-5">
		<div class="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
			<div>
				<h3 class="text-sm font-bold text-amber-950">Deseja alterar suas escolhas?</h3>
				<p class="text-xs text-amber-800">
					Você pode rever seu consentimento para cookies analíticos e de preferências a qualquer
					momento.
				</p>
			</div>
			<button
				type="button"
				onclick={openCookiePreferences}
				class="inline-flex shrink-0 items-center justify-center rounded-xl bg-ink-900 px-4 py-2.5 text-xs font-semibold text-white shadow-sm transition-all hover:bg-slate-800 active:scale-95"
			>
				Gerenciar Preferências de Cookies
			</button>
		</div>
	</div>

	<h2 class="mt-8 text-lg font-semibold text-ink-900">1. O que são Cookies?</h2>
	<p class="mt-2">
		Cookies são pequenos arquivos de texto gravados no seu navegador quando você visita páginas da
		web. Eles permitem que o site reconheça seu dispositivo em acessos futuros, mantenha sua sessão
		conectada, proteja formulários contra ataques fraudulentos (CSRF) e armazene preferências como
		moeda e visualizações.
	</p>

	<h2 class="mt-8 text-lg font-semibold text-ink-900">2. Categorias de Cookies Utilizados</h2>

	<div class="mt-4 space-y-4">
		<div class="rounded-xl border border-slate-200 bg-slate-50 p-4">
			<h3 class="font-semibold text-slate-900">
				A. Cookies Estritamente Necessários (Obrigatórios)
			</h3>
			<p class="mt-1 text-xs text-slate-600">
				Indispensáveis para o funcionamento da plataforma. Sem eles, você não consegue fazer login,
				consultar o endereço confidencial do seu Box, adicionar itens ou solicitar envios. Não podem
				ser desativados em nossos sistemas.
			</p>
		</div>

		<div class="rounded-xl border border-slate-200 bg-slate-50 p-4">
			<h3 class="font-semibold text-slate-900">
				B. Cookies Analíticos e de Desempenho (Opcionais)
			</h3>
			<p class="mt-1 text-xs text-slate-600">
				Permitem contar visitas e fontes de tráfego para que possamos medir e melhorar o desempenho
				da JapanToGo. Todas as métricas são agregadas de forma estritamente anônima.
			</p>
		</div>

		<div class="rounded-xl border border-slate-200 bg-slate-50 p-4">
			<h3 class="font-semibold text-slate-900">C. Cookies de Preferências (Opcionais)</h3>
			<p class="mt-1 text-xs text-slate-600">
				Lembram escolhas feitas por você, tais como filtros nas lojas parceiras ou a moeda
				preferencial de exibição nos cálculos simulados (JPY ou BRL).
			</p>
		</div>
	</div>

	<h2 class="mt-8 text-lg font-semibold text-ink-900">3. Relação de Cookies Ativos</h2>
	<div class="mt-4 overflow-x-auto">
		<table class="w-full text-left text-xs">
			<thead class="border-b border-slate-200 bg-slate-100 font-semibold text-slate-800">
				<tr>
					<th class="p-3">Nome</th>
					<th class="p-3">Categoria</th>
					<th class="p-3">Duração</th>
					<th class="p-3">Finalidade</th>
				</tr>
			</thead>
			<tbody class="divide-y divide-slate-100 text-slate-600">
				<tr>
					<td class="p-3 font-mono font-semibold text-ink-900">access_token</td>
					<td class="p-3">Necessário</td>
					<td class="p-3">15 minutos</td>
					<td class="p-3">Token JWT de autenticação e proteção do painel (HttpOnly).</td>
				</tr>
				<tr>
					<td class="p-3 font-mono font-semibold text-ink-900">refresh_token</td>
					<td class="p-3">Necessário</td>
					<td class="p-3">7 dias</td>
					<td class="p-3">Renovação de sessão segura sem expor credenciais (HttpOnly).</td>
				</tr>
				<tr>
					<td class="p-3 font-mono font-semibold text-ink-900">jtg_cookie_consent</td>
					<td class="p-3">Necessário</td>
					<td class="p-3">365 dias</td>
					<td class="p-3">Guarda a escolha de consentimento do visitante (LGPD/GDPR/APPI).</td>
				</tr>
				<tr>
					<td class="p-3 font-mono font-semibold text-ink-900">jtg_currency_pref</td>
					<td class="p-3">Preferência</td>
					<td class="p-3">180 dias</td>
					<td class="p-3">Memoriza se o usuário prefere visualizar simulações em BRL ou JPY.</td>
				</tr>
			</tbody>
		</table>
	</div>

	<h2 class="mt-8 text-lg font-semibold text-ink-900">4. Como desativar cookies pelo navegador</h2>
	<p class="mt-2">
		Além dos controles oferecidos em nosso banner e nesta página, você pode configurar seu navegador
		para bloquear ou avisar sobre cookies. Observe que a desativação de cookies necessários impedirá
		o login na sua área de cliente.
	</p>
	<ul class="mt-2 list-disc space-y-1 pl-5 text-xs text-slate-600">
		<li>
			<strong>Google Chrome:</strong> Configurações &gt; Privacidade e segurança &gt; Cookies de terceiros.
		</li>
		<li>
			<strong>Mozilla Firefox:</strong> Configurações &gt; Privacidade e Segurança &gt; Cookies e dados
			de sites.
		</li>
		<li>
			<strong>Apple Safari:</strong> Preferências &gt; Privacidade &gt; Bloquear todos os cookies.
		</li>
	</ul>

	<h2 class="mt-8 text-lg font-semibold text-ink-900">5. Dúvidas e Contato</h2>
	<p class="mt-2">
		Em caso de dúvidas sobre nossa utilização de cookies ou tratamento de dados, envie um e-mail
		para{' '}
		<a href="mailto:dpo@japantogo.com" class="font-medium text-brand-600 hover:underline">
			dpo@japantogo.com
		</a>{' '}
		ou acesse nosso formulário na página de{' '}
		<a href="/contato" class="font-medium text-brand-600 hover:underline">Contato</a>.
	</p>
</LegalPage>
