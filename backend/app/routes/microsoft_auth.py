import secrets
from datetime import datetime, timedelta, timezone
from urllib.parse import urlencode

import httpx
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import RedirectResponse
from jose import JWTError, jwt

from app.config import settings
from app.database import supabase
from app.utils import auth_deps


router = APIRouter(prefix="/auth", tags=["microsoft-auth"])


def _require_microsoft_config() -> None:
    required_values = [
        settings.MICROSOFT_CLIENT_ID,
        settings.MICROSOFT_CLIENT_SECRET,
        settings.MICROSOFT_REDIRECT_URI,
    ]

    if not all(required_values):
        raise HTTPException(
            status_code=500,
            detail="Falta configurar las variables de Microsoft OAuth en el .env",
        )


def _build_state(action: str, rol: str | None = None) -> str:
    payload = {
        "action": action,
        "rol": rol,
        "exp": datetime.now(timezone.utc) + timedelta(minutes=10),
        "nonce": secrets.token_urlsafe(16),
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def _read_state(state: str) -> dict:
    try:
        return jwt.decode(state, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    except JWTError as exc:
        raise HTTPException(status_code=400, detail="State de Microsoft invalido o expirado") from exc


def _build_authorize_url(state: str) -> str:
    params = {
        "client_id": settings.MICROSOFT_CLIENT_ID,
        "response_type": "code",
        "redirect_uri": settings.MICROSOFT_REDIRECT_URI,
        "response_mode": "query",
        "scope": settings.MICROSOFT_SCOPES,
        "state": state,
        "prompt": "select_account",
    }
    return (
        f"https://login.microsoftonline.com/"
        f"{settings.MICROSOFT_TENANT_ID}/oauth2/v2.0/authorize?{urlencode(params)}"
    )


def _token_url() -> str:
    return f"https://login.microsoftonline.com/{settings.MICROSOFT_TENANT_ID}/oauth2/v2.0/token"


def _userinfo_url() -> str:
    return "https://graph.microsoft.com/oidc/userinfo"


def _buscar_usuario_por_email(email: str) -> tuple[dict | None, str | None]:
    profe = supabase.table("profesores").select("*").eq("email", email).execute()
    if profe.data:
        return profe.data[0], "profesor"

    est = supabase.table("estudiantes").select("*").eq("email", email).execute()
    if est.data:
        return est.data[0], "estudiante"

    return None, None


def _crear_usuario_microsoft(email: str, nombre: str, rol: str) -> dict:
    tabla = "profesores" if rol == "profesor" else "estudiantes"
    password_hash = auth_deps.get_password_hash(secrets.token_urlsafe(32))

    result = supabase.table(tabla).insert(
        {
            "nombre": nombre,
            "email": email,
            "password_hash": password_hash,
        }
    ).execute()

    if not result.data:
        raise HTTPException(status_code=500, detail="No se pudo crear el usuario con Microsoft")

    return result.data[0]


async def _exchange_code_for_tokens(code: str) -> dict:
    data = {
        "client_id": settings.MICROSOFT_CLIENT_ID,
        "client_secret": settings.MICROSOFT_CLIENT_SECRET,
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": settings.MICROSOFT_REDIRECT_URI,
        "scope": settings.MICROSOFT_SCOPES,
    }

    async with httpx.AsyncClient(timeout=20) as client:
        response = await client.post(_token_url(), data=data)

    if response.status_code != 200:
        raise HTTPException(
            status_code=400,
            detail=f"Microsoft no devolvio tokens validos: {response.text}",
        )

    return response.json()


async def _fetch_userinfo(access_token: str) -> dict:
    headers = {"Authorization": f"Bearer {access_token}"}
    async with httpx.AsyncClient(timeout=20) as client:
        response = await client.get(_userinfo_url(), headers=headers)

    if response.status_code != 200:
        raise HTTPException(
            status_code=400,
            detail=f"No se pudo obtener el perfil de Microsoft: {response.text}",
        )

    return response.json()


def _extract_identity(token_payload: dict, userinfo: dict) -> tuple[str, str]:
    id_token = token_payload.get("id_token")
    id_claims = jwt.get_unverified_claims(id_token) if id_token else {}

    email = (
        userinfo.get("email")
        or id_claims.get("email")
        or id_claims.get("preferred_username")
    )
    nombre = (
        userinfo.get("name")
        or id_claims.get("name")
        or email
    )

    if not email:
        raise HTTPException(
            status_code=400,
            detail="Microsoft no devolvio un email utilizable para este usuario",
        )

    return email.lower(), nombre


def _emitir_jwt_local(usuario: dict, rol: str) -> dict:
    token_data = {"sub": str(usuario["id"]), "rol": rol}
    token = auth_deps.create_access_tokken(token_data)
    return {
        "access_token": token,
        "token_type": "bearer",
        "rol": rol,
        "auth_provider": "microsoft",
        "usuario": {
            "id": usuario["id"],
            "nombre": usuario["nombre"],
            "email": usuario["email"],
        },
    }


def _build_frontend_redirect(payload: dict) -> str:
    query = urlencode(payload)
    return f"{settings.FRONTEND_URL}/?{query}"


def _redirect_with_error(message: str) -> RedirectResponse:
    return RedirectResponse(
        url=_build_frontend_redirect(
            {
                "auth_status": "error",
                "auth_provider": "microsoft",
                "message": message,
            }
        )
    )


def _redirect_with_success(auth_payload: dict) -> RedirectResponse:
    return RedirectResponse(
        url=_build_frontend_redirect(
            {
                "auth_status": "success",
                "auth_provider": auth_payload["auth_provider"],
                "action": auth_payload.get("accion", ""),
                "access_token": auth_payload["access_token"],
                "rol": auth_payload["rol"],
                "email": auth_payload["usuario"]["email"],
                "nombre": auth_payload["usuario"]["nombre"],
            }
        )
    )


@router.get("/microsoft/login")
async def microsoft_login():
    _require_microsoft_config()
    state = _build_state(action="login")
    return RedirectResponse(url=_build_authorize_url(state))


@router.get("/microsoft/registro/{rol}")
async def microsoft_registro(rol: str):
    _require_microsoft_config()

    if rol not in {"profesor", "estudiante"}:
        raise HTTPException(status_code=400, detail="El rol debe ser profesor o estudiante")

    state = _build_state(action="register", rol=rol)
    return RedirectResponse(url=_build_authorize_url(state))


@router.get("/microsoft/callback")
async def microsoft_callback(
    code: str | None = Query(default=None),
    state: str | None = Query(default=None),
    error: str | None = Query(default=None),
    error_description: str | None = Query(default=None),
):
    _require_microsoft_config()

    if error:
        return _redirect_with_error(f"Microsoft devolvio un error: {error_description or error}")

    if not code or not state:
        return _redirect_with_error("Faltan code o state en el callback")

    try:
        state_data = _read_state(state)
        token_payload = await _exchange_code_for_tokens(code)
        userinfo = await _fetch_userinfo(token_payload["access_token"])
        email, nombre = _extract_identity(token_payload, userinfo)

        usuario_existente, rol_existente = _buscar_usuario_por_email(email)
        action = state_data.get("action")
        requested_role = state_data.get("rol")

        if action == "register":
            if usuario_existente:
                return _redirect_with_error("Ese email ya esta registrado en la plataforma")

            usuario = _crear_usuario_microsoft(email, nombre, requested_role)
            auth_payload = {
                **_emitir_jwt_local(usuario, requested_role),
                "accion": "registro",
            }
            return _redirect_with_success(auth_payload)

        if action == "login":
            if not usuario_existente or not rol_existente:
                return _redirect_with_error(
                    "No existe un usuario registrado con ese email. Primero debes registrarte."
                )

            auth_payload = {
                **_emitir_jwt_local(usuario_existente, rol_existente),
                "accion": "login",
            }
            return _redirect_with_success(auth_payload)

        return _redirect_with_error("Accion de Microsoft no reconocida")
    except HTTPException as exc:
        return _redirect_with_error(str(exc.detail))
    except Exception:
        return _redirect_with_error("Ha fallado la autenticacion con Microsoft")
