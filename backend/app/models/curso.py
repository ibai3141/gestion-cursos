from pydantic import BaseModel
from typing import Optional

class CursoBase(BaseModel):
    titulo:str
    profesor_id: int
    descripcion: Optional[str] = None

class CursoCreate(CursoBase):
    pass  # Hereda todo de CursoBase

class CursoResponse(CursoBase):
    id:int
    created_at: str