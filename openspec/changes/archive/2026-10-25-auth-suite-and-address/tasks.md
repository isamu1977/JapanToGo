## 1. Logos Oficiais das Lojas na Landing Page

- [x] 1.1 Atualizar `StoreShowcase.svelte` substituindo os ícones genéricos por marcas vetoriais estilizadas das 8 lojas japonesas (Mercari, Amazon JP, Rakuten, Yahoo! Leilões, AmiAmi, Mandarake, Surugaya, Pokémon Center JP)
- [x] 1.2 Adicionar links diretos para cada loja abrindo em nova aba (`target="_blank" rel="noopener noreferrer"`) e aplicar estilo de card com fundo branco, borda suave e efeito de hover com elevação (`hover:-translate-y-1 hover:shadow-md transition-all`)

## 2. Autenticação Completa e Geração Automática de Suíte (Backend FastAPI)

- [x] 2.1 Adicionar campo opcional `cpf_tax_id` ao modelo de usuário `User` em `backend/app/models/user.py`
- [x] 2.2 Atualizar schemas `UserRegister` e `UserProfile` em `backend/app/schemas/auth.py` para suportar `cpf_tax_id`
- [x] 2.3 Expor rotas `/api/auth/*` como alias em `backend/app/main.py` mantendo compatibilidade com `/api/v1/auth/*`
- [x] 2.4 Executar testes unitários do backend para garantir conformidade de registro, suite code e autenticação

## 3. Layout da Área Logada do Cliente (SvelteKit `(app)`)

- [x] 3.1 Atualizar `AppShell.svelte` com menu lateral padronizado ("Meu Endereço", "Pré-Pedidos", "Minha Suíte", "Envios" e "Sair") e suporte a drawer responsivo
- [x] 3.2 Implementar barra superior destacando o nome do cliente, badge com o código da suíte (`#JTG-1001`) e atalho de perfil

## 4. Tela "Meu Endereço no Japão" (`/app/endereco`)

- [x] 4.1 Atualizar `AddressCard.svelte` com abas para versão em Japonês (com 氏名, 郵便番号, 都道府県, 市区町村, 丁目・番地・号, 建物名・部屋番号, 電話番号) e versão em Alfabeto Romano (Name, Postal Code, Prefecture, City, Street / Number, Building / Unit, Phone)
- [x] 4.2 Implementar botões individuais de cópia com feedback visual ("Copiado!") e botão de ação rápida "Copiar endereço completo formatado"
- [x] 4.3 Refinar a página `/endereco/+page.svelte` com dicas de preenchimento para as lojas

## 5. Validação e Testes

- [x] 5.1 Executar verificação de tipos e linter no frontend (`npm run check` e `npm run lint`)
- [x] 5.2 Executar testes automatizados no frontend (`npm test`) e no backend (`pytest`)
