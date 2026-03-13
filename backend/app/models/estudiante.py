from pydantic import BaseModel
from typing import Optional


class EstudianteBase(BaseModel):
    nombre:str
    email:str

class EstudianteCreate(EstudianteBase):
    password:str
    
class EstudianteResponse(EstudianteBase):
    id:int
    carrera: Optional[str] = None
    anio_ingreso: Optional[str] = None
    created_at: str