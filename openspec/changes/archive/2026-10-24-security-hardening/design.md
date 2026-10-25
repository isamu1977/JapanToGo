## Context

O JapanToGo gerencia bens de alto valor e dados pessoais sensíveis (incluindo CPF para desembaraço aduaneiro no Brasil, endereços e comprovantes de compras).
Para garantir a conformidade com as melhores práticas de segurança da informação (OWASP Top 10) e assegurar a aprovação em gateways de pagamento internacionais (Square, Stripe, Wise), é mandatória a implementação de um conjunto transversal de defesas técnicas denominado **Security Hardening**.

Esta camada atua em 5 pilares críticos:
1. Sessões seguras sem exposição a scripts no cliente (anti-XSS).
2. Validação estrita de escopo de dados (anti-IDOR).
3. Inspeção profunda de arquivos por Magic Bytes e renomeação segura (anti-RCE/armazenamento malicioso).
4. Mitigação de Server-Side Request Forgery (anti-SSRF) com resolução prévia de IP e bloqueio de redes privadas.
5. Limitação de taxa (Rate Limiting) e sanitização/mascaramento de dados em logs de produção.

## Goals / Non-Goals

**Goals:**
- Armazenar JWT de acesso e de renovação exclusivamente em cookies `HttpOnly`, `Secure` e `SameSite=Lax`, eliminando qualquer token ou segredo do `localStorage` no frontend.
- Aplicar hashing de senhas com `bcrypt` ou `argon2id` via Passlib.
- Configurar middleware CORS estrito no FastAPI aceitando exclusivamente a URL oficial do frontend e `localhost` em desenvolvimento.
- Garantir prevenção de IDOR em todas as consultas e mutações de usuários comuns, exigindo filtro `user_id == current_user.id` e retornando HTTP 403 Forbidden para tentativas de acesso não autorizado.
- Validar uploads de arquivos através da leitura de Magic Bytes (`puremagic`/`python-magic`), aceitando unicamente `image/jpeg`, `image/png`, `image/webp` e `application/pdf` (apenas comprovantes).
- Descartar nomes originais de arquivos e renomear com UUIDv4 (`{uuid4()}.{ext}`), aplicando limite rígido de 5 MB por arquivo e servindo estáticos sem capacidade de execução de código.
- Implementar validador anti-SSRF com resolução de DNS para links de produtos japoneses, bloqueando conexões com loopback (127.0.0.1/::1), redes privadas (RFC 1918) e link-local (RFC 3927).
- Aplicar Rate Limiting com `slowapi` nas rotas `/auth/login`, `/auth/register` e `/api/calculator/simulate`.
- Implementar filtro de sanitização em logs para mascarar CPF, senhas e tokens de autenticação antes de qualquer escrita no stdout do Docker/Coolify.

**Non-Goals:**
- Implementação de autenticação multifator (MFA/2FA) via TOTP neste estágio (previsto para fase pós-MVP).
- Antivírus em tempo real (ex: ClamAV) no container; a proteção por Magic Bytes, limites de 5MB, renomeação UUIDv4 e serving estático isolado suprem a barreira de execução no MVP.

## Decisions

### 1. Cookies HttpOnly para Access e Refresh Tokens
- **Decisão**: O backend FastAPI emite dois cookies: `access_token` e `refresh_token`, ambos marcados com `httponly=True`, `samesite="lax"`, e `secure=COOKIE_SECURE` (configurável como `false` para HTTP local e `true` para HTTPS no Coolify). O frontend SvelteKit configura chamadas `fetch` com `credentials: 'include'`.
- **Raciocínio**: Previne roubo de tokens via Cross-Site Scripting (XSS). O `localStorage` é vulnerável a qualquer script malicioso injetado por dependências frontend de terceiros.
- **Alternativas consideradas**:
  - *Access Token no `localStorage`*: Rejeitado por apresentar risco de exfiltração via XSS.

### 2. Validação Estrita de IDOR via Dependências e Consultas Escopadas
- **Decisão**: Todos os endpoints de acesso a recursos individuais (`/api/v1/pre-orders/{id}`, `/api/v1/suite/{id}`, `/api/v1/shipments/{id}`) realizam consulta filtrando explicitamente por `user_id == current_user.id` (exceto para usuários com role `admin`).
- **Raciocínio**: Se um usuário cliente tentar requisitar um ID pertencente a outro cliente, a aplicação detecta e responde imediatamente com `HTTP 403 Forbidden` (ou `HTTP 404 Not Found` para evitar enumeração de recursos).
- **Alternativas consideradas**:
  - *Verificação após carregamento em memória*: Ineficiente e propensa a esquecimentos de verificação em queries complexas.

### 3. Validação de Arquivos por Magic Bytes (`puremagic`) e UUIDv4
- **Decisão**: Utilizar `puremagic` (biblioteca Python pura, sem dependência de DLLs do SO como `libmagic`) para inspecionar os primeiros bytes do arquivo recebido e determinar seu MIME type real. Renomear todo arquivo para `{uuid4()}.{extensão_canônica}` e armazenar em pasta servida estaticamente pelo FastAPI (`StaticFiles`) com headers seguros (`X-Content-Type-Options: nosniff`).
- **Raciocínio**: Extensões de arquivos e cabeçalhos `Content-Type` enviados pelo cliente são facilmente forjados. Magic bytes verificam o conteúdo binário real.
- **Alternativas consideradas**:
  - *python-magic*: Requer biblioteca binária C (`libmagic`), o que pode complicar deploys em contêineres mínimos Alpine/Slim. `puremagic` é 100% Python e altamente confiável.

### 4. Resolução DNS e Prevenção de SSRF
- **Decisão**: Implementar `ssrf_validator.py` que analisa URLs de produtos fornecidas por clientes:
  1. Verifica se o esquema é estritamente `https://`.
  2. Resolve o hostname para endereços IP através de `socket.getaddrinfo`.
  3. Checa cada IP contra listas de exclusão usando o módulo nativo `ipaddress`: `ip.is_private`, `ip.is_loopback`, `ip.is_link_local`, `ip.is_reserved`.
  4. Se qualquer IP pertencer a faixas restritas, aborta a requisição com `HTTP 400 Bad Request`.
- **Raciocínio**: Impede que a aplicação seja usada como proxy para mapear a rede interna do Docker, acessar a API de metadados do host ou varrer a infraestrutura do Coolify.

### 5. Rate Limiting com `slowapi`
- **Decisão**: Adicionar `slowapi` com storage em memória (suficiente para instância única no Coolify) limitando:
  - `/api/v1/auth/login`: 5 requisições por minuto por IP.
  - `/api/v1/auth/register`: 3 requisições por minuto por IP.
  - `/api/v1/calculator/simulate`: 30 requisições por minuto por IP.
- **Raciocínio**: Previne ataques de força bruta de senhas, criação massiva de contas falsas e abuso do simulador de custos.

### 6. Sanitização de Logs e Proteção de PII
- **Decisão**: Configurar um `logging.Filter` customizado no FastAPI que inspeciona mensagens e payloads de log, substituindo padrões de CPF (`\d{3}\.\d{3}\.\d{3}\-\d{2}` ou `\d{11}`) por `***.***.***-**` e mascarando cabeçalhos de autorização e cookies.
- **Raciocínio**: Evita vazamento de dados de clientes em agregadores de logs ou no console do Coolify.

## Risks / Trade-offs

- **[Risco: Bloqueio de cookies em ambientes de desenvolvimento com portas distintas]** → **Mitigação**: O `COOKIE_SECURE` é controlado pela variável de ambiente `COOKIE_SECURE=false` em `localhost`, e `COOKIE_SAMESITE=lax` permite envio de cookies em requisições top-level e CORS com `credentials: 'include'`.
- **[Risco: Falsos positivos no resolvedor anti-SSRF com lojas japonesas usando CDN/Cloudflare]** → **Mitigação**: O validador resolve para o IP público retornado pelo DNS público. Se for um IP público válido na Internet, a requisição é autorizada normalmente.
- **[Risco: Overhead de validação de Magic Bytes]** → **Mitigação**: A leitura de Magic Bytes via `puremagic.from_string()` analisa apenas os primeiros kilobytes do arquivo em buffer de memória, consumindo menos de 1ms por upload.
