## Why

A landing page atual do JapanToGo apresenta inconsistências que afetam a conversão e a experiência do usuário:
1. O Header está visualmente poluído com links contratuais/legais que pertencem ao Footer e exibe o link "Simulador" em duplicidade.
2. O Hero expõe publicamente o endereço do galpão no Japão, o que representa vazamento de dado operacional confidencial que deve ser restrito à área logada do cliente.
3. A seção "Como Funciona" contém incongruências de regras de negócio, mencionando erradamente isenção de taxa ("Sem taxa de 20%") no redirecionamento puro, quando ambas as modalidades praticam taxa de serviço de 20% (com piso de ¥ 2.000).
4. O simulador de custos na landing page exibe a mensagem de erro "Failed to fetch" sempre que a API remota não responde instantaneamente, quebrando a experiência de digitação do visitante.
5. As seções centrais possuem excesso de áreas puramente brancas sem ritmo visual ou profundidade de cards.

Esta refatoração restaura a segurança, precisão negocial, robustez técnica e acabamento visual premium da landing page.

## What Changes

- **Limpeza e Reorganização do Header**:
  - Remoção dos links "Termos de uso", "Privacidade" e "特定商取引法" da barra de navegação superior (mantendo-os exclusivamente no Footer).
  - Correção da duplicação do item "Simulador".
  - Header composto estritamente pelos links âncora: `#como-funciona` ("Como funciona"), `#lojas` ("Lojas"), `#simulador` ("Simulador") e `#faq` ("Dúvidas"), finalizando com os botões "Entrar" (estilo outline/ghost) e "Criar conta" (botão de destaque vermelho).
- **Refatoração da Seção Hero**:
  - Remoção definitiva do card com endereço físico do galpão no Japão da página inicial pública.
  - Substituição por um mockup visual de serviço: card interativo simulando uma encomenda recebida na suíte, com selo de pesagem digital ("Pesado: 350g"), status "Pronto para consolidar" e miniaturas simulando fotos de inspeção em múltiplos ângulos.
  - Atualização dos botões de CTA para: botão primário "Criar Minha Suíte Grátis" e secundário "Simular Custos".
- **Alinhamento de Cópia e Regras de Negócio no "Como Funciona"**:
  - Eliminação de qualquer menção a "Sem taxa de 20%" ou "Quem tem cartão japonês".
  - Padronização da taxa de serviço de 20% (com piso mínimo de ¥ 2.000) para ambas as modalidades.
  - Clarificação do Redirecionamento Puro: cobre recebimento no galpão, pesagem em gramas, inspeção fotográfica em até 5 ângulos e consolidação, aplicando taxa de 20% sobre o valor declarado (mínimo de ¥ 2.000).
  - Clarificação da Compra Assistida: a JapanToGo adquire sob demanda no Japão aplicando 20% de taxa de serviço (mínimo de ¥ 2.000).
- **Simulador de Custos Reativo Local no Cliente**:
  - Eliminação completa de chamadas de rede bloqueantes e erros "Failed to fetch" na Landing Page.
  - Mecanismo de cálculo síncrono/reativo em TypeScript no cliente executando a fórmula oficial:
    * Câmbio JPY/BRL de referência com spread de segurança.
    * Taxa de serviço JapanToGo: `Math.max(2000, valor_jpy * 0.20)` para ambas as modalidades.
    * Frete internacional calculado pelas faixas oficiais do Japan Post (Small Packet até 2kg e EMS express).
    * Estimativa tributária alfandegária brasileira: RTS (60%) e ICMS calculado "por dentro".
  - Recálculo reativo instantâneo conforme o usuário digita ou clica em presets, sem mensagens de falha.
- **Acabamento Visual, Cores e Contraste**:
  - Suavização dos fundos das seções do meio para tonalidades off-white (`bg-slate-50` / `#f8fafc`) com textura sutil e discreta.
  - Aumento da profundidade e elevação dos cards (`shadow-sm`, `hover:shadow-md` e bordas refinadas).

## Capabilities

### New Capabilities
<!-- Nenhuma nova capacidade criada além do escopo de marketing-and-compliance -->

### Modified Capabilities
- `marketing-and-compliance`: Atualização dos requisitos da landing page e simulador de custos para consolidar a navegação focada em âncoras, confidencialidade do galpão no Hero, cálculo reativo local de landed cost e regra unificada de taxa de serviço de 20% (mínimo ¥ 2.000).

## Impact

- **Frontend**:
  - `frontend/src/lib/components/layout/NavHeader.svelte`: Limpeza de links e remoção de duplicidade.
  - `frontend/src/lib/components/landing/HeroSection.svelte`: Substituição do card de endereço pelo mockup de encomenda/suíte com pesagem e fotos de inspeção.
  - `frontend/src/lib/components/landing/WorkflowComparison.svelte`: Correção de cópia, taxas e descrições dos fluxos.
  - `frontend/src/routes/(marketing)/+page.svelte`: Remoção de menções a "Sem taxa de 20%" nas seções de transparência e ajuste de backgrounds.
  - `frontend/src/lib/components/ui/LandedCostCalculator.svelte`: Implementação de cálculo reativo client-side puro com fallbacks graciosos, eliminando "Failed to fetch".
  - `frontend/src/routes/layout.css`: Ajustes de classes utilitárias e texturas de fundo.
- **Backend / APIs**: Sem breaking changes em contratos de backend; os endpoints continuam existindo para as áreas logadas e chamadas administrativas.
