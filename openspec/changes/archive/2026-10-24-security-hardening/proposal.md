## Why

A integridade operacional, os dados de clientes e as transações de compra assistida e redirecionamento do JapanToGo exigem um modelo defensivo de segurança contra vetores comuns da web (OWASP Top 10).
Este módulo de Security Hardening estabelece diretrizes rigorosas para autenticação livre de XSS via Cookies HttpOnly, prevenção de autorização insegura (IDOR), validação de uploads por Magic Bytes com mitigação de RCE, proteção contra SSRF em consultas a produtos japoneses, rate limiting contra ataques de força bruta/DoS e mascaramento de PII em logs de auditoria e contêineres.

## What Changes

- **Sessão e Autenticação Segura**: Eliminação de manipulação de tokens via `localStorage` no frontend; emissão de JWTs exclusivamente através de cookies `HttpOnly`, `Secure` e `SameSite=Lax`; hashing robusto de senhas com Argon2id/Bcrypt; e configuração de middleware CORS restritivo permitindo unicamente origens autorizadas (domínio oficial em produção e localhost em desenvolvimento).
- **Prevenção de IDOR (Insecure Direct Object Reference)**: Garantia de escopo estrito de `user_id` em consultas a suítes (`suite_items`), pré-pedidos (`pre_orders`), fotos de inspeção (`inspection_photos`) e remessas (`shipments`), com bloqueio explícito HTTP 403 Forbidden para requisições de recursos pertencentes a terceiros.
- **Upload Seguro de Arquivos**: Validação de arquivos através de Magic Bytes reais (via `puremagic`/`python-magic`), restrição a tipos seguros (`image/jpeg`, `image/png`, `image/webp` e `application/pdf`), teto rígido de 5 MB por arquivo, descarte de nomes originais com renomeação mandatória para UUIDv4 (`{uuid4()}.{ext}`), e serviço de estáticos sem permissão de execução de scripts dentro do contêiner.
- **Proteção contra SSRF (Server-Side Request Forgery)**: Validação antecipada de URLs com esquema HTTPS obrigatório e resolução de DNS antes do fetch, rejeitando imediatamente requisições destinadas a loopback (127.0.0.1/::1), redes privadas (RFC 1918: 10.0.0.0/8, 172.16.0.0/12, 192.168.0.0/16) e link-local (RFC 3927: 169.254.0.0/16).
- **Rate Limiting e Sanitização**: Proteção contra abusos via `slowapi` nas rotas de login, registro e simulador de custos; mascaramento automático de CPF, senhas e chaves de API nos logs de aplicação e nos contêineres Docker/Coolify.
- **Ambiente de Desenvolvimento e Produção**: Alinhamento com a arquitetura de desenvolvimento local utilizando PostgreSQL nativo do desenvolvedor (`localhost:5432`) sem contêineres locais de banco, mantendo o `docker-compose.yml` e Dockerfiles multi-stage otimizados exclusivamente para o Coolify utilizando `DATABASE_URL` unificada (`postgresql+asyncpg`).

## Capabilities

### New Capabilities
- `security-hardening`: Diretrizes transversais e mecanismos de proteção contra IDOR em todas as rotas do cliente, validação de arquivos por Magic Bytes com UUIDv4, prevenção de SSRF com bloqueio de IPs privados em requisições externas, rate limiting com `slowapi`, e mascaramento de PII/credenciais em logs.

### Modified Capabilities
- `auth-and-suite-management`: Atualização dos requisitos de autenticação e sessão para exigir armazenamento de JWT exclusivamente em Cookies `HttpOnly`, `Secure` e `SameSite=Lax`, sem persistência de access token no `localStorage`, além de middleware CORS restritivo e uso de hashing seguro via passlib.

## Impact

- **Backend**:
  - `app/core/security.py`: Funções para emissão e leitura de cookies de sessão autenticada.
  - `app/core/dependencies.py`: Injeção de dependência para extrair JWT do cookie `HttpOnly` e validação de posse de recursos para prevenção de IDOR.
  - `app/core/config.py`: Variáveis de ambiente para origens CORS, parâmetros de cookies (`COOKIE_SECURE`, `COOKIE_DOMAIN`, `COOKIE_SAMESITE`), e limites de rate limit.
  - `app/services/file_storage.py`: Inclusão de biblioteca de verificação de magic bytes (`puremagic`), limite de 5 MB, e renomeação UUIDv4.
  - `app/services/ssrf_validator.py` (ou em `app/core/security.py`): Utilitário de validação de URL e resolução de IP contra RFC 1918 / RFC 3927.
  - `app/main.py`: Middleware de CORS restritivo, registro do rate limiter (`slowapi`) e filtro de sanitização de logs mascarando CPFs e tokens.
- **Frontend**:
  - `src/lib/api/client.ts`: Configuração com `credentials: 'include'` para envio transparente dos cookies `HttpOnly`, removendo cabeçalhos manuais com `localStorage`.
  - `src/lib/stores/auth.ts`: Gerenciamento do estado da sessão via resposta dos endpoints `/api/v1/auth/me` e `/api/v1/auth/refresh`.
