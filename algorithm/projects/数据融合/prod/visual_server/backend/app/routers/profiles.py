from __future__ import annotations

from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.auth import require_roles
from app.db import get_db
from app.models import ParamDefinition, ParamProfile, ParamProfileValue, User
from app.schemas import ParamDefOut, ProfileCreate, ProfileOut, ProfileUpdate
from app.seed_params import RGB_PREVIEW_VALUES

router = APIRouter(prefix="/api", tags=["profiles"])


@router.get("/param-definitions", response_model=list[ParamDefOut])
def list_defs(
    db: Session = Depends(get_db),
    _: User = Depends(require_roles("configurator", "executor", "viewer", "admin")),
) -> list[ParamDefinition]:
    return list(db.scalars(select(ParamDefinition).order_by(ParamDefinition.stage_id, ParamDefinition.sort_order)))


def _profile_out(db: Session, p: ParamProfile) -> ProfileOut:
    rows = db.scalars(select(ParamProfileValue).where(ParamProfileValue.profile_id == p.id)).all()
    values = {r.param_key: r.value for r in rows}
    return ProfileOut(
        id=p.id,
        name=p.name,
        description=p.description,
        version=p.version,
        preset=p.preset,
        values=values,
        updated_at=p.updated_at,
    )


@router.get("/profiles", response_model=list[ProfileOut])
def list_profiles(
    db: Session = Depends(get_db),
    _: User = Depends(require_roles("configurator", "executor", "viewer", "admin")),
) -> list[ProfileOut]:
    profiles = list(db.scalars(select(ParamProfile).order_by(ParamProfile.id)))
    return [_profile_out(db, p) for p in profiles]


@router.post("/profiles", response_model=ProfileOut)
def create_profile(
    body: ProfileCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_roles("configurator", "admin")),
) -> ProfileOut:
    if db.scalar(select(ParamProfile).where(ParamProfile.name == body.name)):
        raise HTTPException(400, "模板名已存在")
    values = dict(body.values)
    if body.preset == "rgb_preview":
        values.update(RGB_PREVIEW_VALUES)
    p = ParamProfile(name=body.name, description=body.description, preset=body.preset, created_by=user.id)
    db.add(p)
    db.flush()
    for k, v in values.items():
        if db.get(ParamDefinition, k) is None:
            continue
        db.add(ParamProfileValue(profile_id=p.id, param_key=k, value=v))
    db.commit()
    db.refresh(p)
    return _profile_out(db, p)


@router.put("/profiles/{profile_id}", response_model=ProfileOut)
def update_profile(
    profile_id: int,
    body: ProfileUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles("configurator", "admin")),
) -> ProfileOut:
    p = db.get(ParamProfile, profile_id)
    if p is None:
        raise HTTPException(404, "不存在")
    if body.description is not None:
        p.description = body.description
    if body.preset is not None:
        p.preset = body.preset
    if body.values is not None:
        values = dict(body.values)
        if p.preset == "rgb_preview":
            values.update(RGB_PREVIEW_VALUES)
        db.execute(delete(ParamProfileValue).where(ParamProfileValue.profile_id == p.id))
        for k, v in values.items():
            if db.get(ParamDefinition, k) is None:
                continue
            db.add(ParamProfileValue(profile_id=p.id, param_key=k, value=v))
        p.version += 1
    db.commit()
    db.refresh(p)
    return _profile_out(db, p)
