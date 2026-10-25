## 1. Setup e Design Tokens

- [x] 1.1 Atualizar tokens de estilo e utilitários em `frontend/src/routes/layout.css` com paleta refinada (Ink Navy profundo, Carmesim japonês, acentos de foco e sombras suaves)
- [x] 1.2 Criar a estrutura de componentes modulares em `frontend/src/lib/components/landing/`

## 2. Componentes Modulares de UI/UX

- [x] 2.1 Implementar `HeroSection.svelte` com proposta de valor, badges de confiança (galpão em Osaka, balança digital, fotos de inspeção) e card interativo da Suíte com botão de cópia
- [x] 2.2 Implementar `StoreShowcase.svelte` com vitrine visual das lojas japonesas parceiras (Mercari, Amazon JP, Rakuten, Yahoo! Leilões, AmiAmi, Mandarake, Surugaya) e filtros por categoria
- [x] 2.3 Implementar `WorkflowComparison.svelte` com navegação por abas/switcher interativo para Compra Assistida e Redirecionamento Puro, comparativo de taxas e timeline de 4 etapas
- [x] 2.4 Implementar `OperationalPillars.svelte` com visual moderno dos 4 pilares de galpão (pesagem em gramas, inspeção de 5 fotos, consolidação em caixa única e opções de frete)
- [x] 2.5 Aprimorar `LandedCostCalculator.svelte` adicionando barra de presets de produtos com 1 clique (Action Figures, Snacks, Consoles, Cosméticos) e detalhamento visual aprimorado
- [x] 2.6 Implementar `FaqAccordion.svelte` com acordeão expansível acessível (ARIA e navegação por teclado) cobrindo alfândega/RTS, tributação, itens proibidos e prazos de entrega
- [x] 2.7 Implementar `FinalCta.svelte` com chamada para ação de alta conversão e selos de conformidade legal e segurança

## 3. Integração e Validação

- [x] 3.1 Integrar todos os novos componentes na rota principal `frontend/src/routes/(marketing)/+page.svelte`
- [x] 3.2 Aprimorar o cabeçalho de navegação `NavHeader.svelte` com melhor espaçamento, responsividade mobile e navegação âncora suave
- [x] 3.3 Executar verificação de tipos e formatação (`npm run check` e `npm run lint`) no diretório do frontend
- [x] 3.4 Executar a suíte de testes automatizados (`npm test`) para garantir não-regressão
