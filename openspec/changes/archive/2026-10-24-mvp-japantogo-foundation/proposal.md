## Why

Comprar produtos diretamente do Japão frequentemente apresenta barreiras linguísticas, restrições geográficas de entrega e complexidade de conformidade aduaneira e cambial para consumidores internacionais (com foco inicial no Brasil).
O JapanToGo soluciona esse problema estabelecendo uma plataforma integrada de Compra Assistida (代行 - Daikou) e Redirecionamento de Encomendas (Forwarding) com infraestrutura própria de galpão no Japão, pesagem e inspeção visual prévia, suporte a consolidação de frete (Japan Post EMS / Small Packet) e simulação transparente de custos de importação.

## What Changes

- Criação da arquitetura completa e fundação de microsserviços/módulos para o MVP do JapanToGo.
- Criação da modelagem de dados relacional com PostgreSQL 16 e SQLAlchemy 2.0 (Users, PreOrders, PreOrderItems, SuiteItems, InspectionPhotos, Shipments, LegalTermsAcceptance).
- Implementação de autenticação JWT com Refresh Tokens e RBAC (`client` e `admin`).
- Atribuição automática de código único de suíte (`JTG-XXXX`) para cada cliente com visualizador de endereço do galpão em caracteres japoneses e alfabeto latino com cópia em 1 clique.
- Fluxo de Compra Assistida com cálculo automático de taxa de serviço de 20% (com piso mínimo de ¥ 2.000 para pedidos < ¥ 10.000).
- Fluxo de Redirecionamento Puro com comprovante de compra obrigatório e rotina de check-in rápido de encomendas no galpão (pesagem em gramas e upload de até 5 fotos de inspeção).
- Módulo de despacho e consolidação com declaração aduaneira (conteúdo, valor declarado e CPF) e exportação no formato aceito pelo sistema International Mail My Page da Japan Post.
- Landing page pública com simulador interativo de Landed Cost (conversão JPY -> BRL, taxa de serviço, estimativa de frete e projeção de RTS 60% + ICMS por dentro).
- Páginas de conformidade legal exigidas por gateways de pagamento (Termos de Uso, Política de Privacidade e Notação da Lei de Transações Comerciais Especificadas do Japão - Tokushoho).
- Configuração de containerização Docker (Dockerfiles multi-stage) e `docker-compose.yml` reservada para o deploy no Coolify, consumindo um PostgreSQL externo via `DATABASE_URL`.
- Fluxo de desenvolvimento local **sem contêineres de banco de dados**: PostgreSQL nativo do desenvolvedor em `localhost:5432`, bootstrap do database `japantogo` via `createdb` + `alembic upgrade head`, backend com `uvicorn --reload` e frontend com `npm run dev`.
- Configuração de conexão e sessão centralizada em variáveis de ambiente: `DATABASE_URL` (driver assíncrono `postgresql+asyncpg`) como fonte única de verdade — lida tanto pela aplicação quanto pelo Alembic —, variáveis discretas `DB_HOST` / `DB_PORT` / `DB_USER` / `DB_PASSWORD` / `DB_NAME`, `JWT_SECRET` e `COOKIE_DOMAIN`.

## Capabilities

### New Capabilities
- `auth-and-suite-management`: Autenticação JWT (access/refresh tokens), controle de acesso RBAC (`client`/`admin`), geração sequencial/única de `suite_code` (`JTG-XXXX`) e visualização do endereço do galpão japonês em kanji/romaji com injeção do número da suíte.
- `assisted-purchase`: Criação e gestão de pré-pedidos de compra assistida com múltiplos itens/links, cálculo automático da taxa de serviço de 20% (mínimo ¥ 2.000 para pedidos < ¥ 10.000), e fila administrativa de compras com atribuição de código de rastreio doméstico.
- `package-redirection`: Registro de pré-pedidos de redirecionamento puro com upload obrigatório de recibo comercial e fluxo de check-in operacional no galpão (busca rápida por suíte, aferição de peso em gramas, captura/upload de até 5 fotos de inspeção e notificação de entrada no estoque da suíte).
- `shipping-and-consolidation`: Seleção e consolidação de itens estocados na suíte, escolha de modalidade de envio internacional (EMS / Small Packet), preenchimento da declaração aduaneira com CPF do destinatário, fila de despacho no painel de administração e exportador de dados para o sistema International Mail My Page da Japan Post.
- `marketing-and-compliance`: Landing page institucional com branding JapanToGo, simulador interativo de Landed Cost (câmbio JPY/BRL, comissão, estimativa de frete por faixa de peso e projeção de impostos brasileiros RTS + ICMS) e páginas de conformidade legal japonesa (利用規約, プライバシーポリシー, 特定商取引法に基づく表記).

### Modified Capabilities
<!-- Nenhuma capacidade pré-existente alterada (projeto greenfield). -->

## Impact

- **Backend**: Nova aplicação FastAPI (Python 3.12+) com SQLAlchemy 2.0 assíncrono, Pydantic v2, Alembic para migrações e rotas REST organizadas por domínios.
- **Frontend**: Nova aplicação SvelteKit com Tailwind CSS v4, Lucide Svelte e suporte a PWA, estruturada nas rotas `(marketing)`, `(app)` e `(admin)`.
- **Armazenamento**: PostgreSQL 16 para persistência relacional (nativo em `localhost:5432` no desenvolvimento local; serviço externo em produção) e volume de filesystem para fotos de inspeção e comprovantes de compra (`uploads/` local em dev, volume Docker nomeado em produção).
- **Deploy/Infra**: Configuração de Dockerfile multi-stage para backend e frontend e orquestração via `docker-compose.yml` **exclusivamente para o Coolify**, com rede interna e volume persistente de mídia. A conexão com o banco é feita por `DATABASE_URL` — a mesma variável lida pela aplicação e pelo Alembic.
