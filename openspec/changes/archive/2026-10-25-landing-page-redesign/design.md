## Context

A landing page atual do JapanToGo (`frontend/src/routes/(marketing)/+page.svelte`) implementa os requisitos básicos definidos na fase de bootstrap do projeto. No entanto, sua estrutura é estática, carece de identidade visual marcante do Japão contemporâneo, não expõe as lojas parceiras onde os brasileiros mais compram e deixa o usuário sem referências práticas de quanto custa importar produtos típicos (figures, games, cosméticos).

Utilizando os princípios do `ui-ux-pro-max` e os padrões de modern web guidance, este design estabelece a arquitetura visual, de componentes e de interação para transformar a landing page em uma experiência de padrão internacional.

## Goals / Non-Goals

**Goals:**
- **Visual Impact & Japanese Aesthetics**: Implementar um design moderno combinando Ink Navy profundo (`#0b0f19` / `#12162a`), Vermelho Carmesim japonês (`#e11d48`) e contrastes brancos nítidos, com tipografia legível e padrões geométricos sutis.
- **Componentização Modular em Svelte 5**: Quebrar a página em componentes limpos e reutilizáveis em `src/lib/components/landing/`, utilizando Svelte 5 Runes (`$state`, `$derived`).
- **Engajamento Interativo**:
  - Simulador com Presets de 1 clique (Action Figures, Snacks, Consoles, Cosméticos) que preenchem instantaneamente peso e valor.
  - Demonstração interativa da Suíte Japonesa com cópia de endereço em 1 clique e feedback visual.
  - Navegação por abas nos fluxos operacionais (Compra Assistida vs. Redirecionamento).
  - Vitrine de lojas japonesas (Mercari, Rakuten, Amazon JP, Yahoo Leilões, AmiAmi, Mandarake).
  - Acordeão acessível de FAQ respondendo às principais objeções sobre alfândega e frete.
- **Acessibilidade & Desempenho (WCAG 2.1 AA / Core Web Vitals)**:
  - Alvos de toque móvel >= 44x44px.
  - Ícones vetoriais consistentes (`lucide-svelte`), sem uso de emojis estruturais.
  - Respeito a `prefers-reduced-motion` e contraste de cores testado.

**Non-Goals:**
- Não altera APIs de autenticação, suítes ou banco de dados no backend Go.
- Não altera os cálculos fiscais (RTS 60% + ICMS por dentro) definidos na especificação de negócio, apenas aprimora sua apresentação visual e adiciona presets no frontend.
- Não implementa páginas internas do painel administrativo ou do dashboard do usuário (essas mantêm seus componentes atuais).

## Decisions

### 1. Arquitetura Modular de Componentes (Landing Page)
- **Decisão**: Dividir a landing page em componentes especializados em `src/lib/components/landing/`:
  - `HeroSection.svelte`: Manchete, proposta de valor, badges de confiança e card interativo da Suíte.
  - `StoreShowcase.svelte`: Grade de lojas japonesas com filtro por categoria (Anime/Manga, Games, Colecionáveis, Moda & Beleza).
  - `WorkflowComparison.svelte`: Alternador de abas entre Compra Assistida e Redirecionamento Puro, com comparativo de taxas e linha do tempo de 4 passos.
  - `OperationalPillars.svelte`: 4 diferenciais de galpão (Balança digital, Fotos de inspeção, Consolidação de caixas, Fretes expressos/econômicos).
  - `InteractiveCalculatorSection.svelte`: Invólucro com presets de produtos que alimenta o `LandedCostCalculator.svelte`.
  - `FaqAccordion.svelte`: Acordeão com acessibilidade ARIA (`aria-expanded`, teclas Enter/Space) para dúvidas de importação.
  - `TrustBanner.svelte` e `FinalCta.svelte`: Garantias de conformidade legal e chamada para conversão.
- **Alternativa descartada**: Manter tudo dentro de um único `+page.svelte` de mais de 700 linhas, o que dificultaria manutenção, testes e reutilização.

### 2. Estética Visual: "Modern Japan / Tech Precision"
- **Decisão**: Adotar a paleta Japão Contemporâneo com base no `ui-ux-pro-max`:
  - Primária: Deep Ink (`#0B0F19`, `#12162A`) para contrastes e áreas de prestígio tecnológico.
  - Sotaque da Marca: Carmesim/Vermelho Sol Nascente (`#E11D48`, `#BE123C`).
  - Tons de Suporte: Slate neutro (`#F8FAFC`, `#F1F5F9`) para seções claras de fácil leitura, e Verde Esmeralda suave (`#10B981`) para validações de segurança/alfândega.
  - Micro-animações: transições CSS leves (150ms-250ms), sem bibliotecas pesadas de animação em JavaScript para manter o carregamento ultrarrápido (LCP < 1.2s).
- **Alternativa descartada**: Tema brutalista ou excessivamente carregado de efeitos 3D que aumentaria o peso do bundle e prejudicaria usuários em redes móveis brasileiras.

### 3. Presets no Simulador de Custo Aterrissado
- **Decisão**: Adicionar uma barra de seleção rápida de categorias populares no topo do simulador:
  - *Figure de Anime (1/7 Scale)*: ~¥ 12.000, 1.200g, EMS
  - *Box de Snacks / Doces*: ~¥ 3.500, 800g, Small Packet
  - *Console Retro / Portátil*: ~¥ 18.000, 700g, EMS
  - *Skincare / Cosméticos*: ~¥ 6.000, 500g, Small Packet
- **Benefício**: Reduz a fricção cognitiva do usuário que não sabe estimar o peso de um produto em gramas ou o valor médio em ienes.

## Risks / Trade-offs

- **[Risco] Aumento na complexidade do DOM da página inicial**:
  - *Mitigação*: Uso de componentes leves em Svelte 5, evitando dependências externas desnecessárias; renderização sem bloqueio de hidratação.
- **[Risco] Variação cambial no simulador de custos**:
  - *Mitigação*: Manter aviso visível e transparente com tooltip indicando que a cotação JPY/BRL é referencial para planejamento e que os impostos são recolhidos pelos Correios/Receita Federal do Brasil.
- **[Risco] Compatibilidade móvel de tabelas/comparações**:
  - *Mitigação*: Uso de layout mobile-first em cards verticais com transição fluida para colunas em telas maiores (>= 1024px).

## Migration Plan

1. Criar a estrutura de diretório `frontend/src/lib/components/landing/`.
2. Implementar os subcomponentes modulares com Svelte 5 Runes.
3. Atualizar `frontend/src/lib/components/ui/LandedCostCalculator.svelte` com suporte a seleção de presets pré-definidos.
4. Integrar todos os componentes na rota `frontend/src/routes/(marketing)/+page.svelte`.
5. Validar formatação, lint (`npm run lint`), tipos (`npm run check`) e testes automatizados (`npm test`).
