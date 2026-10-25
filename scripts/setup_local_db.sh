#!/usr/bin/env bash
# ---------------------------------------------------------------------------
# JapanToGo - local database bootstrap.
#
# Creates the `japantogo` database on the NATIVE PostgreSQL server that runs
# on localhost:5432 and applies the Alembic migrations.
#
# No Docker container is involved: the local stack is
#   PostgreSQL (native)  ->  uvicorn --reload  ->  npm run dev
#
# Usage:
#   ./scripts/setup_local_db.sh
#
# Optional overrides (environment):
#   DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_NAME, DATABASE_URL
# ---------------------------------------------------------------------------
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$(cd "${SCRIPT_DIR}/../backend" && pwd)"

DB_HOST="${DB_HOST:-localhost}"
DB_PORT="${DB_PORT:-5432}"
DB_USER="${DB_USER:-postgres}"
DB_NAME="${DB_NAME:-japantogo}"

log()  { printf '\033[1;34m[setup]\033[0m %s\n' "$*"; }
fail() { printf '\033[1;31m[setup] ERROR:\033[0m %s\n' "$*" >&2; exit 1; }

# --- Locate psql/createdb ----------------------------------------------------
find_psql() {
  if command -v psql >/dev/null 2>&1; then
    echo "psql"
    return 0
  fi
  local candidate
  candidate="$(ls -d /Applications/Postgres.app/Contents/Versions/*/bin 2>/dev/null | sort -V | tail -1 || true)"
  if [[ -n "${candidate}" && -x "${candidate}/psql" ]]; then
    echo "${candidate}"
    return 0
  fi
  return 1
}

PSQL_BIN_DIR="$(find_psql)" || fail "psql not found. Install PostgreSQL (brew install postgresql@17) or start Postgres.app."
export PATH="${PSQL_BIN_DIR}:${PATH}"

# --- Connection --------------------------------------------------------------
if [[ -n "${DATABASE_URL:-}" ]]; then
  ADMIN_URL="${DATABASE_URL/postgresql+asyncpg/postgresql}"
else
  ADMIN_URL="postgresql://${DB_USER}@${DB_HOST}:${DB_PORT}/postgres"
  if [[ -n "${DB_PASSWORD:-}" ]]; then
    ADMIN_URL="postgresql://${DB_USER}:${DB_PASSWORD}@${DB_HOST}:${DB_PORT}/postgres"
  fi
fi

log "checking PostgreSQL at ${DB_HOST}:${DB_PORT} ..."
if ! psql "${ADMIN_URL}" -tAc 'SELECT 1' >/dev/null 2>&1; then
  fail "cannot connect to PostgreSQL at ${DB_HOST}:${DB_PORT}.
     Make sure the native PostgreSQL server is running, then check DB_USER / DB_PASSWORD in backend/.env"
fi
log "PostgreSQL is reachable."

# --- Create the database -----------------------------------------------------
if psql "${ADMIN_URL}" -tAc "SELECT 1 FROM pg_database WHERE datname='${DB_NAME}'" | grep -q 1; then
  log "database '${DB_NAME}' already exists - skipping creation."
else
  log "creating database '${DB_NAME}' ..."
  # template0 is used because template1 may be in use by other sessions.
  createdb -T template0 "${ADMIN_URL}" "${DB_NAME}" 2>/dev/null \
    || psql "${ADMIN_URL}" -v ON_ERROR_STOP=1 -c "CREATE DATABASE \"${DB_NAME}\" TEMPLATE template0 OWNER \"${DB_USER}\";"
  log "database '${DB_NAME}' created."
fi

# --- Apply migrations --------------------------------------------------------
cd "${BACKEND_DIR}"

if [[ ! -x ".venv/bin/alembic" ]]; then
  fail "backend virtualenv missing. Run: cd backend && python3 -m venv .venv && .venv/bin/pip install -r requirements-dev.txt"
fi

log "applying migrations (alembic upgrade head) ..."
.venv/bin/alembic upgrade head

log "done. Start the stack with:"
log "  cd backend  && .venv/bin/uvicorn app.main:app --reload"
log "  cd frontend && npm run dev"
