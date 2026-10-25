# JapanToGo

**FROM JAPAN TO YOUR DOOR**

Plataforma de *compra assistida* (代行) e *redirecionamento de encomendas*
(forwarding) do Japão para o exterior — com galpão próprio no Japão, pesagem,
inspeção fotográfica, consolidação de frete (Japan Post EMS / Small Packet) e
simulação transparente de custo de importação (*landed cost*).

- **Backend**: FastAPI (Python 3.12) · SQLAlchemy 2.0 async · Alembic · Pydantic v2
- **Frontend**: SvelteKit 2 (Svelte 5) · TypeScript · Tailwind CSS v4 · PWA
- **Banco de dados**: PostgreSQL 16+ (asyncpg)

---

## 1. Ambiente de desenvolvimento (nativo, sem Docker)

> O desenvolvimento local **não** usa contêineres. O PostgreSQL roda nativamente
> na máquina do desenvolvedor em `localhost:5432` e o fluxo é
> `uvicorn --reload` + `npm run dev`.
> O `docker-compose.yml` é reservado para o deploy no Coolify.

### Pré-requisitos

| Ferramenta | Versão | Observação |
|---|---|---|
| Python | 3.12+ | `python3 --version` |
| Node.js | 20+ | `node --version` |
| PostgreSQL | 16+ | nativo ou [Postgres.app](https://postgresapp.com) (roda em `localhost:5432`) |
| `psql` / `createdb` | — | precisam estar no `PATH` (veja Troubleshooting) |

### Passo 1 — Configurar o backend

```bash
cd backend
python3 -m venv .venv
.venv/bin/pip install -r requirements-dev.txt
cp .env.example .env
```

Edite `backend/.env` e ajuste a conexão com o seu PostgreSQL local:

```dotenv
# Fonte única de verdade (driver assíncrono). Usada pela aplicação E pelo Alembic.
DATABASE_URL=postgresql+asyncpg://postgres:sua_senha@localhost:5432/japantogo

# Alternativa: componha a URL a partir destas variáveis (usadas só se
# DATABASE_URL estiver vazia).
DB_HOST=localhost
DB_PORT=5432
DB_USER=postgres
DB_PASSWORD=sua_senha
DB_NAME=japantogo

# Segredo de assinatura dos tokens (gere um novo em produção):
#   python -c "import secrets; print(secrets.token_urlsafe(48))"
JWT_SECRET=dev-secret-key-change-me-0123456789abcdef

# Domínio do cookie HTTP-only de refresh (vazio em localhost).
COOKIE_DOMAIN=
```

> O `alembic.ini` **não** possui `sqlalchemy.url`. O `alembic/env.py` lê a mesma
> `DATABASE_URL` através de `app.core.config.settings`, garantindo que migrações
> e aplicação nunca apontem para bancos diferentes.

### Passo 2 — Criar o banco e aplicar as migrações

```bash
./scripts/setup_local_db.sh
```

O script cria o database `japantogo` no PostgreSQL nativo (`createdb -T template0`)
e executa `alembic upgrade head`. Fazer manualmente:

```bash
createdb -T template0 japantogo
cd backend && .venv/bin/alembic upgrade head
```

### Passo 3 — Subir os servidores

```bash
# Terminal 1 — API
cd backend && .venv/bin/uvicorn app.main:app --reload --port 8000

# Terminal 2 — Web
cd frontend && npm install && npm run dev
```

- API: <http://localhost:8000> · Docs: <http://localhost:8000/docs>
- Web: <http://localhost:5173>

> **Use `localhost` nos dois lados.** A sessão vive em cookies
> `HttpOnly; SameSite=Lax` emitidos pela API (`localhost:8000`). Se você abrir o
> frontend em `127.0.0.1:5173`, o navegador trata `localhost` e `127.0.0.1` como
> *sites* diferentes e não envia os cookies — a sessão é perdida a cada
> recarregamento. Em produção (`app.` + `api.` no mesmo domínio) isso não
> acontece.

### Senhas

A política exige no mínimo 8 caracteres, com pelo menos uma letra e um dígito.
O hash é gerado pelo Passlib com o esquema `bcrypt`.

### Passo 4 — Criar o primeiro administrador

```bash
cd backend
.venv/bin/python -m scripts.create_admin \
  --email admin@japantogo.com \
  --password 'uma-senha-forte'
```

O painel operacional fica em <http://localhost:5173/admin/dashboard>.

### Comandos úteis

```bash
# Backend
cd backend
.venv/bin/alembic revision --autogenerate -m "descricao"   # nova migração
.venv/bin/alembic upgrade head                              # aplica migrações
.venv/bin/alembic downgrade -1                              # desfaz 1 migração
.venv/bin/alembic check                                     # detecta drift
.venv/bin/pytest                                            # testes

# Frontend
cd frontend
npm run check      # svelte-check + lint
npm run test       # testes unitários
npm run build      # build de produção
```

---

## 2. Deploy (Coolify)

O `docker-compose.yml` da raiz é o artefato de deploy. Ele **não** sobe um
contêiner de PostgreSQL: aponte `DATABASE_URL` para a instância gerenciada.

Variáveis obrigatórias no Coolify (o compose falha de forma explícita se
alguma faltar):

| Variável | Uso |
|---|---|
| `DATABASE_URL` | `postgresql+asyncpg://user:pass@host:5432/japantogo` |
| `JWT_SECRET` | assinatura dos tokens de acesso/refresh |
| `COOKIE_DOMAIN` | domínio do cookie de refresh (ex.: `.japantogo.com`) |
| `COOKIE_SECURE` | `true` em produção (HTTPS) |
| `CORS_ORIGINS` | origens do frontend, separadas por vírgula |
| `PUBLIC_API_BASE_URL` | URL pública da API usada pelo navegador |

Validação local do compose (sem subir nada):

```bash
export DATABASE_URL="postgresql+asyncpg://user:pass@host:5432/japantogo"
export JWT_SECRET="uma-chave-de-32-caracteres-ou-mais"
export PUBLIC_API_BASE_URL="https://api.japantogo.com"
docker compose config
```

O volume `uploads` persiste fotos de inspeção e comprovantes entre deploys.
As migrações são aplicadas no deploy com:

```bash
docker compose run --rm backend alembic upgrade head
```

---

## 3. Estrutura do projeto

```
japantogo/
├── docker-compose.yml          # deploy (Coolify)
├── scripts/setup_local_db.sh   # bootstrap do banco local
├── backend/
│   ├── alembic/                # migrações
│   ├── app/
│   │   ├── core/               # settings, db, segurança, RBAC
│   │   ├── models/             # SQLAlchemy 2.0
│   │   ├── schemas/            # Pydantic v2
│   │   ├── services/           # regras de negócio
│   │   └── api/v1/             # rotas REST
│   └── tests/
└── frontend/
    └── src/
        ├── lib/                # api client, stores, componentes
        └── routes/             # (marketing) | (auth) | (app) | (admin)
```

---

## 4. Segurança

A fundação implementa defesas explícitas contra os vetores do OWASP Top 10:

| Vetor | Defesa |
|---|---|
| Roubo de token via XSS | Tokens **exclusivamente** em cookies `HttpOnly`, `SameSite=Lax`, `Secure` em produção. Nada em `localStorage`; as respostas JSON não contêm token. |
| IDOR | Consultas sempre escopadas por `user_id`. Acesso a recurso de outro cliente retorna **403**; inexistente, **404**. |
| Upload malicioso (RCE) | MIME real por **magic bytes** (`puremagic`), extensão canônica, nome **UUIDv4**, teto de **5 MB** (**413**) e re-encode para WebP. |
| SSRF | URLs de produto precisam ser `https`; o host é resolvido e cada IP é checado contra loopback, RFC 1918 e RFC 3927 (`169.254.169.254` incluso). Rejeição com **400**. |
| Força bruta / abuso | Rate limiting por IP: login **5/min**, registro **3/min**, simulador **30/min** (**429** + headers). |
| Vazamento de PII em logs | `logging.Filter` global que mascara CPF (`***.***.***-**`), senhas, `Bearer`, JWTs e chaves de API antes do stdout. |

Os testes de regressão ficam em `backend/tests/test_security.py`.

---

## 5. Troubleshooting

**`psql: command not found`** — o Postgres.app instala os binários fora do `PATH`:

```bash
export PATH="/Applications/Postgres.app/Contents/Versions/17/bin:$PATH"
```

**`cannot connect to PostgreSQL at localhost:5432`** — o servidor nativo não está
rodando. No Postgres.app clique em *Start*; via Homebrew: `brew services start postgresql@17`.

**`error: source database "template1" is being accessed by other users`** —
o `setup_local_db.sh` já usa `createdb -T template0` para contornar isso.

**CORS / cookie em desenvolvimento** — o frontend roda em `localhost:5173` e a
API em `localhost:8000`. Garanta que `CORS_ORIGINS` inclua
`http://localhost:5173` e que `COOKIE_SECURE=false` localmente.
