from pydantic import BaseModel
from typing import Optional


class InscripcionBase(BaseModel):
    estudiante_id : int
    curso_id: int
    calificacion: Optional[float] = None  # ← Nota: mejor float que str

class InscripcionCreate(InscripcionBase):
    pass

class InscripcionResponse(InscripcionBase):
    id:int
    created_at:str
    fecha_inscripcion: str  # ← Nombre correcto de la columna
