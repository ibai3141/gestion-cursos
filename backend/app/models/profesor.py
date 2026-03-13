from pydantic import BaseModel
from typing import Optional


# Esto es lo que tienen en común
class ProfesorBase(BaseModel):  # ← HEREDA de BaseModel
    nombre: str
    email: str

# Para crear (incluye password)
class ProfesorCreate(ProfesorBase):  # ← HEREDA de ProfesorBase
    password: str

# Para responder (sin password, con datos de la BD)
class ProfesorResponse(ProfesorBase):  # ← HEREDA de ProfesorBase
    id: int
    especialidad: Optional[str] = None
    biografia: Optional[str] = None
    created_at: str