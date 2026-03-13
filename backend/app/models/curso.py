from pydantic import BaseModel
from typing import Optional

class CursoBase(BaseModel):
    titulo: str
    descripcion: Optional[str] = None

class CursoCreate(CursoBase):
    pass  

class CursoResponse(CursoBase):
    id: int
    profesor_id: int  
    created_at: str