## Context

A landing page do JapanToGo é a porta de entrada para novos usuários. Embora a estrutura modular inicial tenha sido estabelecida, a análise de uso e as diretrizes do usuário revelaram 5 pontos críticos que comprometem a conversão, a segurança e a precisão do negócio:
1. O Header acumula links institucionais/legais do rodapé e duplica o "Simulador".
2. O Hero vaza o endereço físico do galpão em Osaka para o público não autenticado.
3. A seção "Como funciona" contradiz o modelo tarifário da empresa ao alegar "Sem taxa de 20%" para redirecionamento.
4. O simulador de custos quebra com "Failed to fetch" caso o backend não esteja ativo ou haja latência de rede.
5. As seções centrais apresentam áreas brancas desprovidas de textura e profundidade tátil nos cards.

Este documento detalha as decisões técnicas para resolver cada um desses itens de forma definitiva no ecossistema SvelteKit.

## Goals / Non-Goals

**Goals:**
- **Navegação Cirúrgica no Header**:
  - Exibir apenas âncoras na Home: `#como-funciona`, `#lojas`, `#simulador`, `#faq`.
  - Botão "Entrar" com estilo ghost/outline e "Criar conta" como destaque primário vermelho.
  - Eliminar duplicidade de links e remover termos legais da barra superior (restritos ao footer).
- **Proteção do Galpão & Mockup Visual de Suíte**:
  - Remover completamente o CEP e logradouro japonês do código da Home pública.
  - Criar um componente de demonstração da encomenda na suíte com badge digital de balança (`Pesado: 350g`), status operacional e miniaturas simuladas de fotos de inspeção fotográfica em múltiplos ângulos.
  - Botões de CTA: "Criar Minha Suíte Grátis" e "Simular Custos".
- **Alinhamento Negocial das Modalidades**:
  - Unificar a cobrança da taxa de serviço em 20% (piso de ¥ 2.000) em Compra Assistida e Redirecionamento Puro.
  - Descrever com clareza o valor agregado do Redirecionamento: recebimento, pesagem precisa, inspeção de até 5 fotos e consolidação.
- **Simulação 100% Reativa e Resiliente (Client-Side)**:
  - Criar o módulo `frontend/src/lib/utils/calculator.ts` em TypeScript puro espelhando a lógica do backend (`fee_calculator.py`).
  - Execução reativa síncrona: nenhuma dependência de rede síncrona na Landing Page, garantindo latência zero e eliminando o erro "Failed to fetch".
- **Acabamento Visual & Profundidade**:
  - Aplicação de fundo off-white (`#F8FAFC` / `bg-slate-50`) com padrão sutil de pontos (*dot-pattern* SVG/CSS).
  - Elevação e suavidade nos cards com `shadow-sm`, transições suaves no hover (`hover:shadow-md`) e bordas nítidas.

**Non-Goals:**
- Não altera a tabela de fretes ou alíquotas fiscais oficiais já definidas (RTS 60% e ICMS por dentro).
- Não altera o endereço real do galpão fornecido no dashboard autenticado (`/app/suite`) aos clientes cadastrados.
- Não remove as páginas legais (`/termos`, `/privacidade`, `/tokushoho`), apenas as mantém em seus locais adequados no Footer e links contextuais.

## Decisions

### 1. Header Focado em Conversão e Âncoras
- **Decisão**: Em `NavHeader.svelte`, filtrar os links de forma que, na landing page (`currentPath === '/'`), apenas os 4 atalhos de seção sejam renderizados:
  - `#como-funciona` (Como funciona)
  - `#lojas` (Lojas)
  - `#simulador` (Simulador)
  - `#faq` (Dúvidas)
  Os links de termos e privacidade continuam disponíveis globalmente no componente `Footer.svelte`.
  O botão "Entrar" adota a classe `btn-secondary border-slate-300 hover:border-slate-400 bg-transparent` (ghost/outline) e "Criar conta" adota `btn-primary` com destaque vermelho carmesim.

### 2. Mockup da Suíte no Hero (Confidencialidade do Galpão)
- **Decisão**: Substituir o card de texto com endereço por um card interativo de inspeção:
  - Header do Card: Código da Suíte `#JTG-1001` + Tag "Galpão Osaka".
  - Encomenda em Destaque: Card do pacote com título ilustrativo ("Nendoroid / Figure Colecionável - Mercari JP"), código de rastreio interno e etiqueta "Pronto para envio".
  - Selo de Balança Digital: Badge destacado em verde esmeralda com ícone de balança e texto `Pesado: 350g`.
  - Galeria de Inspeção: 4 miniaturas simulando fotos reais tiradas pela equipe (Frente, Verso, Lacre da Caixa, Etiqueta) com indicador "4 de 5 fotos".
  - Benefício de Confidencialidade: O endereço real do galpão só é acessível após login na suíte privativa do usuário, prevenindo uso indevido por spammers ou robôs de busca.

### 3. Modelo de Tarifas Unificado no "Como Funciona"
- **Decisão**:
  - Atualizar o modelo de dados em `WorkflowComparison.svelte` e no resumo de `fees` em `+page.svelte`.
  - `assisted`: 20% de taxa de serviço (piso de ¥ 2.000). A JapanToGo compra no Japão com métodos de pagamento locais.
  - `forwarding`: 20% de taxa de serviço sobre o valor declarado (piso de ¥ 2.000). O cliente compra diretamente e a JapanToGo cuida do recebimento, pesagem em gramas, inspeção de até 5 fotos e consolidação.
  - Remover qualquer frase contendo "Sem taxa de 20%" ou menção a "Quem tem cartão japonês".

### 4. Módulo de Cálculo Client-Side (`calculator.ts`)
- **Decisão**: Implementar `calculateLandedCostClient(...)` em TypeScript:
  - Cotação: taxa base JPY/BRL (0.038) + spread (0.02) = taxa efetiva ~0.03876.
  - Taxa JapanToGo: `Math.max(2000, Math.round(itemPriceJpy * 0.20))` para ambas as modalidades.
  - Frete EMS: Base ¥ 3.000 (primeiros 500g) + ¥ 600 por faixa adicional de 500g.
  - Frete Small Packet: Base ¥ 1.500 (primeiros 500g) + ¥ 300 por faixa adicional de 500g (limite 2.000g).
  - Impostos: RTS = 60% do valor aduaneiro (BRL); ICMS = 18% sobre base com imposto ("por dentro").
  - Atualização síncrona sem disparar requisições assíncronas que possam resultar em "Failed to fetch".

### 5. Texturas e Ritmo Visual das Seções
- **Decisão**:
  - Criar a classe utilitária `.bg-dots` em `layout.css`:
    ```css
    .bg-dots {
      background-color: #f8fafc;
      background-image: radial-gradient(#cbd5e1 0.75px, transparent 0.75px);
      background-size: 20px 20px;
    }
    ```
  - Intercalar seções claras com `.bg-dots` e bordas sutis para quebrar a monotonia do fundo puramente branco.
  - Adicionar sombras suaves e transição nos cards (`shadow-sm hover:shadow-md hover:-translate-y-0.5 transition-all duration-200`).

## Risks / Trade-offs

- **[Risco] Divergência entre cálculo do frontend e do backend**:
  - *Mitigação*: Testes unitários no frontend comparando os resultados do TypeScript com os cenários oficiais do `fee_calculator.py` (ex: figure de ¥ 8.000 / 1000g).
- **[Risco] Navegação âncora em páginas internas**:
  - *Mitigação*: Na `NavHeader.svelte`, se a rota atual não for `/`, os links âncora prefixam com `/#` (ex: `/#simulador`), permitindo retornar à Home na seção desejada.
