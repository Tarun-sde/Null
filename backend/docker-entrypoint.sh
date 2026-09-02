#!/bin/sh
set -eu

python -m alembic upgrade head

python - <<'PY'
import os
from app.db.session import SessionLocal
from sqlalchemy import text
from app.seed.seed import seed_database

db = SessionLocal()
try:
    has_equipment = db.execute(text("SELECT to_regclass('public.equipment') IS NOT NULL")).scalar()
    if not has_equipment:
        seed_database(db, reset=True)
    else:
        equipment_count = db.execute(text("SELECT COUNT(*) FROM equipment")).scalar()
        if equipment_count == 0:
            seed_database(db, reset=True)
finally:
    db.close()
PY

python - <<'PY'
import os
from app.db.session import SessionLocal
from app.models.user import User
from app.core.security import hash_password

admin_email = os.getenv("ADMIN_EMAIL", "")
admin_password = os.getenv("ADMIN_PASSWORD", "")

if admin_email and admin_password:
    db = SessionLocal()
    try:
        existing = db.query(User).filter(User.email == admin_email).first()
        if not existing:
            user = User(
                email=admin_email,
                hashed_password=hash_password(admin_password),
                role="admin",
                is_active=True,
            )
            db.add(user)
            db.commit()
            print(f"Admin user seeded: {admin_email}")
        else:
            print(f"Admin user already exists: {admin_email}")
    finally:
        db.close()
else:
    print("ADMIN_EMAIL or ADMIN_PASSWORD not set — skipping admin seed")
PY

exec python -m uvicorn main:app --host 0.0.0.0 --port 8000
