"""Create the first administrator account.

Usage:
    cd backend
    .venv/bin/python -m scripts.create_admin --email admin@japantogo.com --password 'strong-password'
"""

from __future__ import annotations

import argparse
import asyncio
import sys

from sqlalchemy import select

from app.core.database import AsyncSessionLocal
from app.core.security import hash_password
from app.models.base import UserRole
from app.models.user import User


async def create_admin(email: str, password: str, full_name: str, phone: str) -> int:
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(User).where(User.email == email.lower().strip())
        )
        if result.scalar_one_or_none() is not None:
            print(f"An account with e-mail {email} already exists.")
            return 1

        admin = User(
            email=email.lower().strip(),
            hashed_password=hash_password(password),
            full_name=full_name,
            phone=phone,
            role=UserRole.admin,
            is_active=True,
            suite_code=None,
        )
        session.add(admin)
        await session.commit()

    print(f"Administrator {email} created.")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Create a JapanToGo administrator.")
    parser.add_argument("--email", required=True)
    parser.add_argument("--password", required=True)
    parser.add_argument("--name", default="JapanToGo Admin")
    parser.add_argument("--phone", default="+81-6-0000-0000")
    args = parser.parse_args()

    if len(args.password) < 8:
        print("The password must have at least 8 characters.", file=sys.stderr)
        return 2

    return asyncio.run(
        create_admin(args.email, args.password, args.name, args.phone)
    )


if __name__ == "__main__":
    raise SystemExit(main())
