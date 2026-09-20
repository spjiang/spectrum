from __future__ import annotations

from sqlalchemy.orm import Session

from app.models import SystemSetting

RBAC_KEY = "rbac_menus"
ROLES = ("admin", "configurator", "executor", "viewer")
MENU_KEYS = (
    "execute",
    "profiles",
    "jobs",
    "worker",
    "health",
    "settings",
    "cli",
    "inspect",
    "users",
    "roles",
    "permissions",
)
ADMIN_LOCK = ("users", "roles", "permissions")

DEFAULT_MENUS: dict[str, list[str]] = {
    "admin": list(MENU_KEYS),
    "configurator": ["profiles", "jobs", "settings", "inspect"],
    "executor": ["execute", "profiles", "jobs", "inspect"],
    "viewer": ["profiles", "jobs", "inspect"],
}


def _clean_menus(keys: list[str]) -> list[str]:
    allowed = set(MENU_KEYS)
    out: list[str] = []
    for key in keys:
        if key in allowed and key not in out:
            out.append(key)
    return out


def default_mapping() -> dict[str, list[str]]:
    return {role: list(keys) for role, keys in DEFAULT_MENUS.items()}


def load_mapping(db: Session) -> dict[str, list[str]]:
    mapping = default_mapping()
    row = db.get(SystemSetting, RBAC_KEY)
    raw = row.value if row is not None and isinstance(row.value, dict) else {}
    seen: set[str] = set()
    for role in ROLES:
        saved = raw.get(role)
        if isinstance(saved, list):
            seen.update(str(x) for x in saved)
            mapping[role] = _clean_menus([str(x) for x in saved])
    mapping["admin"] = list(MENU_KEYS)
    for role in ROLES:
        if role == "admin":
            continue
        for key in DEFAULT_MENUS[role]:
            if key not in seen and key not in mapping[role]:
                mapping[role].append(key)
        mapping[role] = _clean_menus(mapping[role])
    return mapping


def save_mapping(db: Session, mapping: dict[str, list[str]]) -> dict[str, list[str]]:
    cleaned = default_mapping()
    for role in ROLES:
        cleaned[role] = _clean_menus(mapping.get(role) or cleaned[role])
    cleaned["admin"] = list(MENU_KEYS)
    for key in ADMIN_LOCK:
        if key not in cleaned["admin"]:
            cleaned["admin"].append(key)
    row = db.get(SystemSetting, RBAC_KEY)
    if row is None:
        db.add(SystemSetting(key=RBAC_KEY, value=cleaned))
    else:
        row.value = cleaned
    db.commit()
    return cleaned


def set_role_menus(db: Session, role: str, menus: list[str]) -> dict[str, list[str]]:
    mapping = load_mapping(db)
    if role not in ROLES:
        return mapping
    if role == "admin":
        mapping[role] = list(MENU_KEYS)
    else:
        mapping[role] = _clean_menus(menus)
    return save_mapping(db, mapping)


def set_permission_roles(db: Session, menu_key: str, roles: list[str]) -> dict[str, list[str]]:
    if menu_key not in MENU_KEYS:
        return load_mapping(db)
    wanted = {r for r in roles if r in ROLES}
    wanted.add("admin")
    mapping = load_mapping(db)
    for role in ROLES:
        current = set(mapping[role])
        if role in wanted:
            current.add(menu_key)
        elif role != "admin":
            current.discard(menu_key)
        mapping[role] = _clean_menus(list(current))
    mapping["admin"] = list(MENU_KEYS)
    return save_mapping(db, mapping)
