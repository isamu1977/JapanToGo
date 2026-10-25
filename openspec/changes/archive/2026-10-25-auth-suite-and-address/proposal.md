## Why

Com a landing page revitalizada e as regras tarifárias consolidadas, o próximo passo essencial da experiência do usuário é fechar o ciclo de aquisição: permitir que o visitante descubra as lojas oficiais com suas identidades visuais autênticas, crie sua conta de forma segura com geração atômica da sua suíte exclusiva (`JTG-1001`), e acerte na hora de cadastrar o endereço do galpão nas lojas japonesas através da tela "Meu Endereço no Japão".

## What Changes

- **Logos Oficiais das Lojas na Landing Page**:
  - Substituição dos ícones genéricos na vitrine de lojas por marcas visuais estilizadas com fundo transparente das 8 lojas principais: Mercari, Amazon JP, Rakuten, Yahoo! Leilões, AmiAmi, Mandarake, Surugaya e Pokémon Center JP.
  - Estilização refinada dos cards com fundo branco, borda suave (`border-slate-200/80`), elevação no hover (`hover:-translate-y-1 hover:shadow-md transition-all`) e link direto para o site da loja abrindo em nova aba (`target="_blank" rel="noopener noreferrer"`).
- **Autenticação Segura e Modelo de Usuário Atualizado (Backend FastAPI + PostgreSQL)**:
  - Inclusão do campo opcional `cpf_tax_id` no modelo `User` e schemas de registro/perfil (opcional no cadastro, exigido na remessa internacional).
  - Suporte às rotas `/api/auth/register`, `/api/auth/login`, `/api/auth/logout` e `/api/auth/me` (com compatibilidade com `/api/v1/auth/*`).
  - Geração atômica de `suite_code` sequencial (`JTG-1001`, `JTG-1002`, etc.) via sequence PostgreSQL.
  - Sessão emitida exclusivamente via cookies `HttpOnly`, `SameSite=Lax` e `Secure`.
- **Layout Responsivo da Área Logada (SvelteKit `(app)`)**:
  - Reestruturação do dashboard do cliente com sidebar retrátil no mobile e navegação desktop limpa.
  - Menu lateral padronizado: "Meu Endereço" (galpão), "Pré-Pedidos" (carrinho), "Minha Suíte" (estoque), "Envios" (avião) e "Sair".
  - Barra superior destacando o nome do cliente, badge com o código da suíte (`#JTG-1001`) e atalho de perfil.
- **Tela "Meu Endereço no Japão" (`/app/endereco`)**:
  - Exibição em duas abas/colunas: Versão em Japonês (氏名, 郵便番号, 都道府県, 市区町村, 丁目・番地・号, 建物名・部屋番号 com `#SUITE_CODE`, 電話番号) e Versão em Alfabeto Romano (Name, Postal Code, Prefecture, City, Street/Number, Building/Unit com `#SUITE_CODE`, Phone).
  - Botão individual de "Copiar" por linha com feedback visual imediato ("Copiado!") e botão de ação rápida "Copiar endereço completo formatado".

## Capabilities

### New Capabilities
<!-- Nenhuma nova capacidade necessária; utiliza o modelo existente de capabilities -->

### Modified Capabilities
- `auth-and-suite-management`: Adiciona suporte ao campo opcional `cpf_tax_id`, rotas `/api/auth/*` e aprimoramento da tela de endereço com cópia individual e formatada em abas bilaterais (Japonês e Romano).
- `marketing-and-compliance`: Atualiza a vitrine de lojas para exibir marcas visuais autênticas e links externos para cada marketplace japonês.

## Impact

- **Backend**:
  - `backend/app/models/user.py`: Campo `cpf_tax_id` opcional na tabela `users`.
  - `backend/app/schemas/auth.py`: Inclusão de `cpf_tax_id` nos schemas `UserRegister` e `UserProfile`.
  - `backend/app/main.py`: Mapeamento das rotas `/api/auth/*` como alias direto para a autenticação.
- **Frontend**:
  - `frontend/src/lib/components/landing/StoreShowcase.svelte`: Logos SVG/marcas estilizadas e links externos.
  - `frontend/src/lib/components/layout/AppShell.svelte`: Novo layout da área logada com topbar e sidebar atualizadas.
  - `frontend/src/routes/(app)/endereco/+page.svelte` e `frontend/src/lib/components/ui/AddressCard.svelte`: Nova interface de endereço com abas Japonês / Romano e botões de cópia individual.
