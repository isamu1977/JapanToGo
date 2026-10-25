# syntax=docker/dockerfile:1

# ---------- builder ----------
# Node 22 is required by SvelteKit 3 (it relies on `Promise.withResolvers`).
FROM node:22-alpine AS builder

WORKDIR /app

ENV NODE_ENV=development

# Install dependencies first so the layer is cached across source changes.
COPY package.json package-lock.json* ./
RUN if [ -f package-lock.json ]; then npm ci; else npm install; fi

COPY . .

RUN npm run build


# ---------- production dependencies ----------
FROM builder AS prod-deps
RUN npm prune --omit=dev


# ---------- runtime ----------
FROM node:22-alpine AS runtime

ENV NODE_ENV=production \
    PORT=3000 \
    HOST=0.0.0.0

WORKDIR /app

COPY --from=prod-deps /app/node_modules ./node_modules
COPY --from=builder /app/build ./build
COPY --from=builder /app/package.json ./package.json

# The official node images already ship a `node` user (uid/gid 1000).
RUN chown -R node:node /app

USER node

EXPOSE 3000

HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=5 \
    CMD wget -qO- http://localhost:3000/healthz || exit 1

CMD ["node", "build"]
