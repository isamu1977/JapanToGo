<script lang="ts">
	import LegalPage from '#lib/components/layout/LegalPage.svelte';
</script>

<LegalPage title="Política de privacidade" titleJa="プライバシーポリシー" updated="24/10/2026">
	<h2 class="text-lg font-semibold text-ink-900">1. Dados que coletamos</h2>
	<p class="mt-2">
		Coletamos apenas o necessário para operar o serviço: nome completo, endereço de e-mail,
		telefone, endereço de entrega no Brasil, códigos de identificação fiscal (CPF) para a declaração
		aduaneira, itens solicitados, comprovantes de compra e fotos de inspeção enviadas por você.
	</p>
	<p class="mt-2" lang="ja">
		当社はサービス提供に必要な情報のみを取得します。具体的には、氏名、メールアドレス、電話番号、
		ブラジルの配送先住所、税関申告のための CPF、購入依頼の内容、購入証明書、およびお客様が送信した
		検査写真です。
	</p>

	<h2 class="mt-8 text-lg font-semibold text-ink-900">2. Como usamos os dados</h2>
	<ul class="mt-2 list-disc space-y-1 pl-5">
		<li>Executar compras assistidas e consolidar envios.</li>
		<li>Emitir declaração aduaneira e documentos de transporte.</li>
		<li>Comunicar o andamento das encomendas e o status dos pré-pedidos.</li>
		<li>Cumprir obrigações legais, fiscais e aduaneiras aplicáveis.</li>
	</ul>
	<p class="mt-2" lang="ja">
		上記の情報は、購入代行の実行、発送物のとりまとめ、税関申告書の作成、輸送書類の作成、
		および当社に課される法令上の義務を守るために利用します。
	</p>

	<h2 class="mt-8 text-lg font-semibold text-ink-900">3. Base legal e compartilhamento</h2>
	<p class="mt-2">
		Tratamos seus dados com base no consentimento e na execução do contrato. Compartilhamos
		informações estritamente necessárias com as lojas de origem (quando aplicável), com a Japan Post
		no momento do despacho e com autoridades aduaneiras e fiscais quando exigido por lei. Não
		vendemos seus dados.
	</p>
	<p class="mt-2" lang="ja">
		当社は同意および契約の履行を根拠として個人情報を取り扱います。販売店舗および Japan Post
		（発送時）、および法令に基づく税関・税務当局に対して、必要な範囲でのみ情報を提供します。
		お客様の個人情報を販売することはありません。
	</p>

	<h2 class="mt-8 text-lg font-semibold text-ink-900">4. Retenção</h2>
	<p class="mt-2">
		Mantemos os dados da conta enquanto ela estiver ativa. Fotos de inspeção e comprovantes de
		compra são guardados por até 24 meses após o despacho, salvo obrigação legal de guarda por prazo
		maior.
	</p>
	<p class="mt-2" lang="ja">
		アカウントが有効な間、データを保持します。検査写真および購入証明書は、発送後 24
		か月間保存します。ただし、法令により長い保存が求められる場合を除きます。
	</p>

	<h2 class="mt-8 text-lg font-semibold text-ink-900">5. Seus direitos</h2>
	<p class="mt-2">
		Você pode solicitar acesso, correção, portabilidade ou exclusão dos seus dados, bem como revogar
		o consentimento, escrevendo para contato@japantogo.com. A exclusão da conta remove os dados
		pessoais, preservando apenas os registros que a lei exige conservar.
	</p>
	<p class="mt-2" lang="ja">
		お客様は、データの開示、訂正、開示請求、削除および同意の撤回を contato@japantogo.com
		へのメールによって請求できます。アカウントの削除後も、法令の定めにより
		保存を求められる記録を除き、個人情報は削除されます。
	</p>

	<h2 class="mt-8 text-lg font-semibold text-ink-900">6. Segurança</h2>
	<p class="mt-2">
		Senhas são armazenadas com hash bcrypt, sessões usam tokens JWT e as senhas de sessão ficam em
		cookies HTTP-only. Fotos e comprovantes ficam em armazenamento com controle de acesso restrito à
		operação.
	</p>
	<p class="mt-2" lang="ja">
		パスワードは bcrypt によるハッシュで保存され、セッションには JWT
		を使用し、リフレッシュトークンは HTTP-only Cookie
		で管理します。写真および証明書は、運用担当者だけがアクセスできる領域に保存します。
	</p>

	<h2 class="mt-8 text-lg font-semibold text-ink-900">7. Alterações desta política</h2>
	<p class="mt-2">
		Esta política pode ser atualizada. A data da última atualização aparece no topo desta página.
	</p>
	<p class="mt-2" lang="ja">
		本ポリシーは随時更新される場合があります。最終更新日は本ページ冒頭に記載しています。
	</p>

	<h2 class="mt-8 text-lg font-semibold text-ink-900">
		8. Encarregado de Proteção de Dados (DPO / LGPD & GDPR)
	</h2>
	<p class="mt-2">
		Para esclarecimentos sobre o tratamento de seus dados pessoais ou para exercer qualquer um dos
		direitos previstos na Lei Geral de Proteção de Dados (LGPD - Lei nº 13.709/2018), no Regulamento
		Geral sobre a Proteção de Dados da União Europeia (GDPR) ou na legislação japonesa (APPI), entre
		em contato com nosso Encarregado de Proteção de Dados (DPO):
	</p>
	<div class="mt-3 space-y-1 rounded-xl border border-slate-200 bg-slate-50 p-4 text-xs">
		<p class="font-semibold text-slate-800">Encarregado pelo Tratamento de Dados Pessoais (DPO)</p>
		<p>
			E-mail oficial: <a
				href="mailto:dpo@japantogo.com"
				class="font-medium text-brand-600 hover:underline">dpo@japantogo.com</a
			>
			(ou
			<a href="mailto:contato@japantogo.com" class="font-medium text-brand-600 hover:underline"
				>contato@japantogo.com</a
			>)
		</p>
		<p>Prazo de resposta: Até 15 (quinze) dias nos termos do art. 19 da LGPD.</p>
	</div>
	<p class="mt-2" lang="ja">
		個人情報の取り扱いに関するご質問、または個人情報保護法（APPI）、ブラジルLGPD、EU一般データ保護規則（GDPR）に基づく開示・訂正等のご請求は、データ保護担当者（dpo@japantogo.com）までお問い合わせください。
	</p>
</LegalPage>
