from pydantic import BaseModel
from typing import Optional


class InscripcionBase(BaseModel):
    curso_id: int

class InscripcionCreate(InscripcionBase):
    pass  

class InscripcionResponse(InscripcionBase):
    id: int
    estudiante_id: int 
    fecha_inscripcion: str
    calificacion: Optional[float] = None
