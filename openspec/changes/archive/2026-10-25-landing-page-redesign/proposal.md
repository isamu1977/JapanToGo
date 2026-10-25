## Why

A landing page atual do JapanToGo possui uma estrutura funcional básica, mas visualmente genérica, com baixa densidade de prova social, ausência de vitrine interativa de lojas japonesas parceiras e fluxo estático que não transmite a sofisticação, credibilidade e precisão necessárias para um serviço de intermediação e redirecionamento de compras internacionais (Japão para Brasil).

Para aumentar a taxa de conversão de visitantes em clientes cadastrados e mitigar o receio de importação, é essencial uma reformulação de UI/UX de alto padrão: estética moderna inspirada no minimalismo japonês e tecnologia contemporânea, elementos visuais ricos (galpão em Osaka, simulação visual da suíte, catálogo das lojas mais populares), simulador de custos interativo com presets rápidos e seções estratégicas de conversão (FAQ interativo, passo a passo visual e garantias de segurança).

## What Changes

- **Hero Section Premium & Dinâmica**: Novo visual impactante com estética japonesa moderna (Navy Ink profundo, Carmesim vibrante, acentos em dourado suave), micro-badge de galpão verificado no Japão, demonstração interativa da suíte do cliente com botão de cópia de endereço, e métricas em destaque.
- **Showcase Interativo de Lojas Japonesas Suportadas**: Vitrine visual das principais lojas onde os clientes compram (Mercari, Amazon JP, Rakuten, Yahoo! Leilões, AmiAmi, Mandarake, Pokémon Center JP, Surugaya) com tags de categorias (animes, games, moda, colecionáveis, cosméticos).
- **Comparador Visual de Fluxos (Compra Assistida vs. Redirecionamento)**: Navegação por abas/switcher interativo detalhando passo a passo os dois caminhos, prazos, taxas e vantagens de cada modalidade com visual em linha do tempo.
- **Simulador de Custo Aterrissado Turbinado com Presets de Produtos**: Presets rápidos com 1 clique (ex: Figure colecionável, Caixa de snacks, Console portátil, Cosméticos japoneses) que pré-configuram preço em ienes e peso estimado, além de detalhamento gráfico das parcelas de imposto (RTS 60% e ICMS) e taxas.
- **Destaque dos Diferenciais Operacionais**: Seção visual destacando pesagem em gramas em balança digital, até 5 fotos de inspeção em alta resolução, consolidação inteligente de múltiplos pacotes em uma caixa e suporte bilíngue (Português/Japonês).
- **Seção de FAQ & Mitigação de Dúvidas de Importação**: Acordeão expansível com respostas diretas sobre Remessa Conforme / tributação aduaneira brasileira, itens proibidos pela Japan Post / EMS, prazos médios de entrega e formas de pagamento.
- **Refinamento Global de Micro-interações e Acessibilidade (WCAG 2.1 AA)**: Feedback tátil/hover em todos os elementos clicáveis, contraste em conformidade, respeito a `prefers-reduced-motion` e design responsivo otimizado para dispositivos móveis (375px a telas ultrawide).

## Capabilities

### New Capabilities
<!-- Nenhuma nova capacidade requerida além do escopo de marketing e experiência do usuário -->

### Modified Capabilities
- `marketing-and-compliance`: Expansão dos requisitos da Landing Page para incorporar vitrine interativa de lojas japonesas, presets de cálculo no simulador de custos, visualização guiada dos fluxos operacionais (daikou vs forwarding) e componente interativo de FAQ de importação.

## Impact

- **Frontend**: Atualização de `frontend/src/routes/(marketing)/+page.svelte`, criação de novos componentes modulares em `frontend/src/lib/components/landing/` (ex: `StoreShowcase.svelte`, `WorkflowComparison.svelte`, `FaqAccordion.svelte`, `SuiteMockup.svelte`), e aprimoramento de `frontend/src/lib/components/ui/LandedCostCalculator.svelte`.
- **CSS / Tokens**: Enriquecimento de tokens no `@theme` em `frontend/src/routes/layout.css` (gradientes sutis, sombras refinadas e micro-animações).
- **Sem impactos negativos em Backend/APIs**: Todas as modificações são de camada de apresentação e experiência de usuário no cliente SvelteKit.
