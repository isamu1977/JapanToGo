## Context

O JapãoToGo atua na ponte entre e-commerce japonês e clientes brasileiros. Três engrenagens fundamentais precisam operar em harmonia:
1. Na vitrine pública, os clientes devem reconhecer imediatamente as marcas visuais autênticas das lojas onde desejam comprar (Mercari, Amazon JP, Rakuten, etc.).
2. No cadastro, o cliente deve receber automaticamente uma suíte única (`JTG-XXXX`) emitida por sequence atômica do PostgreSQL, com sessão segura em cookies HttpOnly.
3. Na área logada, o cliente precisa saber exatamente como preencher cada campo de endereço nos checkouts japoneses, com suporte bilíngue (Kanji/Kana para lojas locais e Romaji para Amazon JP) e cópia em 1 clique com feedback visual.

## Goals / Non-Goals

**Goals:**
- **Identidade Visual Autêntica nas Lojas**:
  - Renderizar marcas vetoriais estilizadas das 8 lojas com paletas oficiais e links externos funcionais em nova aba.
- **Autenticação Segura & Geração de Suíte**:
  - Adicionar o campo `cpf_tax_id` ao modelo de dados do usuário e schemas.
  - Oferecer suporte a rotas `/api/auth/*` e `/api/v1/auth/*` para registro, login, logout e `/me`.
  - Garantir emissão atômica de `suite_code` a partir de `JTG-1001`.
  - Manter tokens exclusivamente em cookies `HttpOnly`, `SameSite=Lax`.
- **Layout Responsivo da Área Logada (`AppShell.svelte`)**:
  - Sidebar retrátil com gaveta móvel acessível.
  - Navegação padronizada: "Meu Endereço", "Pré-Pedidos", "Minha Suíte", "Envios" e "Sair".
  - Topbar com identificação do cliente e badge em destaque `#JTG-XXXX`.
- **Tela "Meu Endereço no Japão" (`/app/endereco`)**:
  - Layout dividido em abas/colunas: Japonês e Alfabeto Romano.
  - Mapeamento exato dos campos solicitados pelos formulários japoneses.
  - Botão de cópia individual por linha e botão de cópia de endereço completo formatado.

**Non-Goals:**
- Não altera o fluxo interno de cálculo de frete ou simulação fiscal.
- Não substitui o backend FastAPI por outro framework; mantém SQLAlchemy assíncrono e PostgreSQL.

## Decisions

### 1. Marcas Visuais Vetoriais das Lojas Japonesas
- **Decisão**: Criar componente/emblemas SVG inline para cada uma das 8 lojas em `StoreShowcase.svelte`, garantindo nitidez em qualquer densidade de pixels (Retina display), transparência perfeita e sem dependência de imagens externas que possam quebrar.
- **Lojas mapeadas**:
  - Mercari: `https://jp.mercari.com`
  - Amazon Japan: `https://www.amazon.co.jp`
  - Rakuten: `https://www.rakuten.co.jp`
  - Yahoo! Leilões: `https://auctions.yahoo.co.jp`
  - AmiAmi: `https://www.amiami.com`
  - Mandarake: `https://order.mandarake.co.jp`
  - Surugaya: `https://www.suruga-ya.jp`
  - Pokémon Center Japan: `https://www.pokemoncenter-online.com`

### 2. Atributo `cpf_tax_id` e Roteamento `/api/auth`
- **Decisão**:
  - Adicionar `cpf_tax_id: Mapped[str | None] = mapped_column(String(14), nullable=True)` em `User`.
  - Incluir `cpf_tax_id` opcional nos schemas `UserRegister` e `UserProfile`.
  - Em `backend/app/main.py`, incluir `api_router` ou `auth.router` sob prefixo `/api` para atender tanto chamadas `/api/auth/...` quanto `/api/v1/auth/...`.

### 3. AppShell com Identidade do Cliente
- **Decisão**:
  - Redesenhar `AppShell.svelte`:
    - Menu lateral com itens atualizados:
      - `Meu Endereço`: `/endereco` (ícone `Warehouse` / `MapPin`)
      - `Pré-Pedidos`: `/pre-pedidos` (ícone `ShoppingBag`)
      - `Minha Suíte`: `/suite` (ícone `Boxes`)
      - `Envios`: `/envios` (ícone `Plane`)
    - Header com nome do cliente, badge `#JTG-XXXX` em destaque com fundo carmesim/navy e status ativo.
    - Suporte a gaveta mobile com botão de menu e fechamento ao clicar fora ou navegar.

### 4. Tela de Endereço Bilíngue com Cópia Rápida
- **Decisão**:
  - Estruturar `AddressCard.svelte` com seletor de abas (Japonês vs. Alfabeto Romano) ou exibição lado a lado em telas grandes (>= 1024px).
  - Cada linha de endereço contém:
    - Rótulo (ex: `氏名` / `Nome` ou `郵便番号` / `CEP`)
    - Valor com fonte monoespaçada legível
    - Botão de cópia individual com ícone que se transforma temporariamente em `Check` ("Copiado!")
  - No rodapé do card, botão primário "Copiar endereço completo formatado" que gera o bloco de texto exato pronto para colar.

## Risks / Trade-offs

- **[Risco] Formatação do nome do cliente em sites japoneses**:
  - *Mitigação*: Exibir instrução clara recomendando o preenchimento do nome e da suíte exatamente como exibido na tela para garantir o check-in automático pela equipe do galpão.
