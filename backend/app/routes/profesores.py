'''
GET	/profesores/	Listar todos los profesores (público)
GET	/profesores/{id}	Ver detalle de un profesor (público, con sus cursos)
PUT	/profesores/perfil	Actualizar perfil del profesor autenticado
'''

from app.utils import auth_deps
from fastapi import APIRouter, HTTPException, Depends
from app.database import supabase
from app.models import profesor
from typing import List

router = APIRouter(prefix="/profesores", tags=["profesores"])

@router.get("/", response_model=List[profesor.ProfesorResponse])
async def get_profesores(usuario = Depends(auth_deps.get_current_user)):
    
    if usuario["rol"] == "profesor" or usuario["rol"] == "estudiante":
        result = supabase.table("profesores").select("*").execute()
    else:
        raise HTTPException(status_code=403, detail="Rol no autorizado")

    return result.data
    
