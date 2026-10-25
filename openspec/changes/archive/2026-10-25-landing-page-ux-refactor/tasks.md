## 1. Limpeza e Reorganização do Header

- [x] 1.1 Atualizar `NavHeader.svelte` removendo links legais da navegação superior (termos, privacidade, tokushoho mantidos exclusivamente no footer)
- [x] 1.2 Corrigir duplicação do link "Simulador" e manter apenas os 4 links âncora ("Como funciona", "Lojas", "Simulador", "Dúvidas")
- [x] 1.3 Estilizar botões de ação do Header: "Entrar" como outline/ghost e "Criar conta" com destaque primário vermelho

## 2. Refatoração da Seção Hero

- [x] 2.1 Remover completamente o card com endereço físico e CEP do galpão no Japão de `HeroSection.svelte`
- [x] 2.2 Implementar mockup visual do serviço no Hero com card de encomenda na suíte, badge digital de balança ("Pesado: 350g") e miniaturas de fotos de inspeção em múltiplos ângulos
- [x] 2.3 Atualizar os botões de ação do Hero para "Criar Minha Suíte Grátis" (primário) e "Simular Custos" (secundário com âncora `#simulador`)

## 3. Correção de Cópia e Regras de Negócio no "Como Funciona"

- [x] 3.1 Atualizar `WorkflowComparison.svelte` eliminando as menções a "Sem taxa de 20%" e "Quem tem cartão japonês"
- [x] 3.2 Ajustar a modalidade "Redirecionamento puro" esclarecendo que cobre recebimento, pesagem, inspeção fotográfica (até 5 ângulos) e consolidação, aplicando a taxa de serviço de 20% (mínimo ¥ 2.000)
- [x] 3.3 Ajustar a modalidade "Compra assistida" mantendo a taxa de serviço de 20% (mínimo ¥ 2.000)
- [x] 3.4 Atualizar o resumo de taxas em `frontend/src/routes/(marketing)/+page.svelte` para refletir as taxas corretas

## 4. Simulador de Custos Reativo no Cliente

- [x] 4.1 Criar utilitário de cálculo local em TypeScript `frontend/src/lib/utils/calculator.ts` espelhando as regras de câmbio, taxa mínima, faixas do Japan Post e tributos brasileiros (RTS 60% e ICMS por dentro)
- [x] 4.2 Refatorar `LandedCostCalculator.svelte` para cálculo reativo instantâneo no cliente sem depender de rede síncrona na Landing Page, eliminando o erro "Failed to fetch"

## 5. Acabamento Visual, Cores e Contraste

- [x] 5.1 Atualizar `frontend/src/routes/layout.css` adicionando textura sutil de fundo (classe `.bg-dots`) e refinando sombras suaves dos cards
- [x] 5.2 Aplicar tom off-white com textura de fundo nas seções intermediárias da landing page e reforçar profundidade e transições nos cards

## 6. Verificação e Testes

- [x] 6.1 Executar verificação de tipos e linter (`npm run check` e `npm run lint`) no frontend
- [x] 6.2 Executar suíte de testes do frontend (`npm test`) garantindo não-regressão
