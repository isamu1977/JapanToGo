<script lang="ts">
	import LegalPage from '#lib/components/layout/LegalPage.svelte';

	const seller = {
		name: 'ジャパン・トゥ・ゴー / JapanToGo',
		representative: '代表者 / Representative: Bruno Nakashima',
		address: '〒 群馬県',
		addressEn: 'Gunma, JAPAN',
		phone: '+81-0000-0000',
		email: 'contato@japantogo.com',
		established: '2026'
	};

	const rows = [
		{ label: '販売事業者 / Seller', value: seller.name },
		{ label: '代表者 / Representative', value: seller.representative },
		{ label: '所在地 / Address', value: `${seller.address} / ${seller.addressEn}` },
		{ label: '電話番号 / Telephone', value: seller.phone },
		{ label: 'メールアドレス / E-mail', value: seller.email },
		{ label: '設立 / Established', value: seller.established },
		{
			label: '商品代金以外の必要料金 / Additional charges',
			value:
				'サービス手数料 20%（最低 ¥2,000）、国際送料、関税・輸入税（受取人が負担するブラジル輸入税）'
		},
		{
			label: '支払方法 / Payment methods',
			value:
				'銀行振込（Bank transfer）、クレジットカード（Credit card）、国際送金（International remittance）'
		},
		{
			label: '支払時期 / Payment timing',
			value:
				'商品購入完了後、発送前にお支払い / Payment before dispatch, after the purchase is completed'
		},
		{
			label: '引渡時期 / Delivery',
			value: '発送確認後 7〜15 営業日程度 / Approximately 7 to 15 business days after dispatch'
		},
		{
			label: '返品・キャンセル / Returns and cancellation',
			value:
				'購入確定前はキャンセル可。購入確定後は各販売店の返品方針に従います / Free cancellation before the purchase is completed; afterwards the retailer policy applies'
		},
		{
			label: '個人情報の取得 / Privacy',
			value: '可 — Our Privacy Policy（/privacidade）'
		}
	];
</script>

<LegalPage
	title="特定商取引法に基づく表記"
	titleJa="Notification based on the Specified Commercial Transactions Act"
	updated="24/10/2026"
>
	<p class="text-slate-600">
		Esta página divulga as informações exigidas pela lei japonesa de transações comerciais
		especificadas (特定商取引法), necessária para a habilitação da plataforma junto aos gateways de
		pagamento.
	</p>
	<p class="mt-2" lang="ja">
		本ページは、特定商取引法に基づく表記です。決済サービス提供のため、特定商取引法の規定に基づく開示に準じます。
	</p>

	<dl class="mt-8 divide-y divide-slate-200">
		{#each rows as row (row.label)}
			<div class="grid gap-1 py-4 sm:grid-cols-3 sm:gap-4">
				<dt class="text-sm font-medium text-ink-900 sm:col-span-1">{row.label}</dt>
				<dd class="text-sm text-slate-600 sm:col-span-2">{row.value}</dd>
			</div>
		{/each}
	</dl>

	<div class="mt-8 rounded-xl bg-slate-50 p-4 text-sm text-slate-600">
		<p>
			Service fees are charged only on assisted purchases. For pure forwarding the client buys
			directly and only the international shipping plus any customs duties apply.
		</p>
		<p class="mt-2" lang="ja">
			サービス手数料は購入代行の場合のみ発生します。転送のみの場合は、国際送料と関税が
			適用されます。
		</p>
	</div>

	<p class="mt-6 text-sm text-slate-500">
		<a href="/privacidade" class="font-medium text-brand-700 underline">Política de privacidade</a>
		·
		<a href="/termos" class="font-medium text-brand-700 underline">Termos de uso</a>
	</p>
</LegalPage>
