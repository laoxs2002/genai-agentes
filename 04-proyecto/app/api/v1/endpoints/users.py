from fastapi import APIRouter, Request, HTTPException

from app.schemas.requests import UserProfileUpdate
from app.schemas.responses import UserProfile

router = APIRouter(prefix="/users", tags=["users"])

# Namespace for profile in PostgresStore: ("perfil", user_id)
PROFILE_NAMESPACE = "perfil"
PROFILE_KEY = "profile"


@router.get("/{user_id}/profile", response_model=UserProfile)
async def get_profile(user_id: str, request: Request):
    store = request.app.state.store
    namespace = (PROFILE_NAMESPACE, user_id)
    try:
        value = store.get(namespace, PROFILE_KEY)
    except Exception:
        value = None
    if value is None:
        return UserProfile(user_id=user_id, nombre=None, producto=None, preferencias=None)
    v = value.value if hasattr(value, "value") else value
    if isinstance(v, dict):
        pref = v.get("preferencias")
        return UserProfile(
            user_id=user_id,
            nombre=v.get("nombre"),
            producto=v.get("producto"),
            preferencias=pref,  # puede ser dict (guardado por agente) o str
        )
    return UserProfile(user_id=user_id, nombre=None, producto=None, preferencias=None)


@router.put("/{user_id}/profile", response_model=UserProfile)
async def update_profile(user_id: str, body: UserProfileUpdate, request: Request):
    store = request.app.state.store
    namespace = (PROFILE_NAMESPACE, user_id)
    try:
        existing = store.get(namespace, PROFILE_KEY)
    except Exception:
        existing = None
    current = {}
    if existing is not None:
        v = existing.value if hasattr(existing, "value") else existing
        if isinstance(v, dict):
            current = v
    update = body.model_dump(exclude_unset=True)
    current.update(update)
    store.put(namespace, PROFILE_KEY, current)
    return UserProfile(
        user_id=user_id,
        nombre=current.get("nombre"),
        producto=current.get("producto"),
        preferencias=current.get("preferencias"),
    )
