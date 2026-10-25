<script lang="ts">
	import LegalPage from '#lib/components/layout/LegalPage.svelte';
</script>

<LegalPage
	title="Itens Proibidos e Restritos"
	titleJa="国際郵便における禁制品・航空危険物 (Prohibited & Restricted Items)"
	updated="25/10/2026"
>
	<div class="rounded-xl border border-red-200 bg-red-50/70 p-4 text-xs text-red-950">
		<div class="flex items-start gap-3">
			<svg
				class="mt-0.5 h-5 w-5 shrink-0 text-red-600"
				fill="none"
				viewBox="0 0 24 24"
				stroke="currentColor"
			>
				<path
					stroke-linecap="round"
					stroke-linejoin="round"
					stroke-width="2"
					d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
				/>
			</svg>
			<div class="leading-relaxed">
				<strong class="font-bold"
					>Aviso Crítico de Segurança Aeronáutica (UPU / ICAO / IATA):</strong
				>
				O despacho aéreo de substâncias inflamáveis, baterias soltas ou produtos restritos é proibido
				por tratados internacionais e pela Lei Postal do Japão. Pacotes contendo itens proibidos são confiscados
				no raio-X do aeroporto de Kansai (KIX) ou devolvidos ao galpão com custos adicionais por conta
				do cliente.
			</div>
		</div>
	</div>

	<h2 class="mt-8 text-lg font-semibold text-ink-900">1. Categorias Absolutamente Proibidas</h2>
	<p class="mt-2 text-slate-600">
		Os itens listados abaixo <strong>não podem</strong> ser despachados sob nenhuma modalidade postal
		internacional (EMS, Small Packet ou Courier aéreo):
	</p>

	<div class="mt-4 grid gap-4 sm:grid-cols-2">
		<!-- Baterias -->
		<div class="rounded-xl border border-slate-200 bg-slate-50 p-4">
			<div class="flex items-center gap-2">
				<span class="rounded-lg bg-red-100 p-1.5 text-red-700">🔋</span>
				<h3 class="text-sm font-bold text-slate-900">Baterias de Lítio e Power Banks</h3>
			</div>
			<ul class="mt-2 list-disc space-y-1 pl-4 text-xs text-slate-600">
				<li>Baterias de lítio soltas ou avulsas (pilhas recarregáveis, 18650, etc.).</li>
				<li>Power banks e carregadores portáteis portáteis de qualquer capacidade.</li>
				<li>
					<em>Exceção:</em> Baterias instaladas <strong>dentro</strong> do próprio equipamento (ex: console
					Switch ou smartphone) são permitidas com limite de até 2 baterias por embalagem e sob declaração
					IATA.
				</li>
			</ul>
		</div>

		<!-- Líquidos Inflamáveis e Perfumes -->
		<div class="rounded-xl border border-slate-200 bg-slate-50 p-4">
			<div class="flex items-center gap-2">
				<span class="rounded-lg bg-red-100 p-1.5 text-red-700">🔥</span>
				<h3 class="text-sm font-bold text-slate-900">Líquidos Inflamáveis e Perfumes</h3>
			</div>
			<ul class="mt-2 list-disc space-y-1 pl-4 text-xs text-slate-600">
				<li>Perfumes, colônias, eau de toilette e difusores aromáticos com álcool.</li>
				<li>Esmaltes de unha, removedores à base de acetona e tintas a óleo.</li>
				<li>Isqueiros, fluídos Zippo, fósforos e gás para maçarico.</li>
				<li>Bebidas alcoólicas com teor superior a 24% ABV.</li>
			</ul>
		</div>

		<!-- Aerossóis e Sprays -->
		<div class="rounded-xl border border-slate-200 bg-slate-50 p-4">
			<div class="flex items-center gap-2">
				<span class="rounded-lg bg-red-100 p-1.5 text-red-700">💨</span>
				<h3 class="text-sm font-bold text-slate-900">Aerossóis e Gases Comprimidos</h3>
			</div>
			<ul class="mt-2 list-disc space-y-1 pl-4 text-xs text-slate-600">
				<li>Desodorantes e protetores solares em embalagem aerossol sob pressão.</li>
				<li>Sprays fixadores de cabelo, tintas spray e lubrificantes WD-40.</li>
				<li>Cilindros de CO2 para armas de airsoft ou sifão culinário.</li>
			</ul>
		</div>

		<!-- Alimentos Perecíveis e Carnes -->
		<div class="rounded-xl border border-slate-200 bg-slate-50 p-4">
			<div class="flex items-center gap-2">
				<span class="rounded-lg bg-red-100 p-1.5 text-red-700">🥩</span>
				<h3 class="text-sm font-bold text-slate-900">Alimentos de Origem Animal e Sementes</h3>
			</div>
			<ul class="mt-2 list-disc space-y-1 pl-4 text-xs text-slate-600">
				<li>Carnes secas, jerky, embutidos e derivados suínos ou bovinos.</li>
				<li>Lácteos frescos e queijos não pasteurizados.</li>
				<li>Sementes não processadas, mudas de plantas e terra fértil (Vigiagro).</li>
				<li>
					<em>Permitido:</em> Doces industrializados, chocolates, matcha, snacks e temperos secos lacrados.
				</li>
			</ul>
		</div>

		<!-- Armas e Simulacros -->
		<div class="rounded-xl border border-slate-200 bg-slate-50 p-4">
			<div class="flex items-center gap-2">
				<span class="rounded-lg bg-red-100 p-1.5 text-red-700">⚔️</span>
				<h3 class="text-sm font-bold text-slate-900">Armas, Lâminas e Simulacros</h3>
			</div>
			<ul class="mt-2 list-disc space-y-1 pl-4 text-xs text-slate-600">
				<li>Katanas reais com fio de corte e facas táticas de combate.</li>
				<li>Marcadores de paintball e réplicas de airsoft que imitem armas de fogo reais.</li>
				<li>Munições, pólvora e materiais pirotécnicos (fogos de artifício).</li>
			</ul>
		</div>

		<!-- Sanções e Mercadorias Ilegais -->
		<div class="rounded-xl border border-slate-200 bg-slate-50 p-4">
			<div class="flex items-center gap-2">
				<span class="rounded-lg bg-red-100 p-1.5 text-red-700">🚫</span>
				<h3 class="text-sm font-bold text-slate-900">Sanções Internacionais e Produtos Ilícitos</h3>
			</div>
			<ul class="mt-2 list-disc space-y-1 pl-4 text-xs text-slate-600">
				<li>Produtos falsificados, réplicas não autorizadas ou que violem marcas registradas.</li>
				<li>Substâncias entorpecentes, medicamentos sob controle especial e canabinoides.</li>
				<li>
					Itens oriundos de países sob sanção das Nações Unidas ou do Ministério das Finanças do
					Japão (MOF).
				</li>
			</ul>
		</div>
	</div>

	<h2 class="mt-8 text-lg font-semibold text-ink-900">2. Procedimento de Triagem no Galpão</h2>
	<p class="mt-2 text-slate-600">
		Ao receber qualquer pacote em Osaka, a equipe da JapanToGo abre a caixa externa de entrega para
		pesagem precisa e conferência visual. Caso nossa inspeção detecte um item proibido para frete
		aéreo:
	</p>
	<ol class="mt-2 list-decimal space-y-1.5 pl-5 text-xs text-slate-600">
		<li>
			O cliente é notificado imediatamente no painel do cliente e por e-mail com fotos do item
			restrito.
		</li>
		<li>
			O cliente poderá optar por devolver o item ao vendedor japonês (se dentro do prazo de
			devolução da loja, mediante pagamento da postagem local) ou autorizar o descarte ambiental
			seguro no Japão.
		</li>
		<li>
			Caso a encomenda contenha itens mistos (permitidos e proibidos), podemos segregar e
			descartar/devolver apenas a parte não despachável, liberando os demais produtos para envio
			normal.
		</li>
	</ol>

	<h2 class="mt-8 text-lg font-semibold text-ink-900">3. Dúvidas antes de comprar?</h2>
	<p class="mt-2 text-slate-600">
		Se você estiver na dúvida se determinado item pode ser enviado (ex: cosmético com pequena fração
		de álcool, console antigo ou colecionável metálico), fale com nossa equipe antes de efetuar a
		compra através da nossa página de <a
			href="/contato"
			class="font-semibold text-brand-600 hover:underline">Contato</a
		> ou via WhatsApp.
	</p>
</LegalPage>
