from __future__ import annotations

from sqlalchemy import select, text
from sqlalchemy.orm import Session

from app.auth import ensure_role, hash_password
from app.config import Settings
from app.models import User
from app.seed_params import seed_param_definitions
from app.services.mq import check_rabbitmq


def bootstrap(db: Session, settings: Settings) -> None:
    for name in ("admin", "configurator", "executor", "viewer"):
        ensure_role(db, name)
    db.commit()
    seed_param_definitions(db)
    user = db.scalar(select(User).where(User.username == settings.bootstrap_admin_user))
    if user is None:
        admin = User(
            username=settings.bootstrap_admin_user,
            password_hash=hash_password(settings.bootstrap_admin_password),
            is_active=True,
        )
        admin.roles.append(ensure_role(db, "admin"))
        db.add(admin)
        db.commit()


def health_payload(db: Session, settings: Settings) -> dict:
    try:
        db.execute(text("SELECT 1"))
        pg = "ok"
    except Exception as exc:  # noqa: BLE001
        pg = f"error: {exc}"
    rq = check_rabbitmq(settings.rabbitmq_url)
    status = "ok" if pg == "ok" and rq == "ok" else "degraded"
    return {"status": status, "postgres": pg, "rabbitmq": rq}
