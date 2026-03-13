from app.utils import auth_deps
from fastapi import APIRouter, HTTPException, Depends
from app.database import supabase
from app.models import curso

router = APIRouter(prefix="/cursos", tags=["cursos"])

@router.get("/")
async def get_cursos(usuario = Depends(auth_deps.get_current_user)):
    
    if usuario["rol"] == "profesor":
        resul = supabase.table("cursos").select("*").eq("profesor_id", usuario["sub"]).execute()
        
    else:
        resul = supabase.table("incripciones").select("*").eq("estudiante_id", usuario["sub"]).execute()
    
    
    
    return resul.data


@router.post("/", response_model=curso.CursoResponse)
async def altaCurso(curso_data : curso.CursoCreate,usuario = Depends(auth_deps.get_current_user)):
    
    if usuario["rol"] == "profesor":
        
        resul = supabase.table("cursos").insert({
            "titulo": curso_data.titulo,
            "descripcion": curso_data.descripcion, 
            "profesor_id": usuario["sub"]  
            }).execute()
    else:
        raise HTTPException(status_code=403,detail="solo los profes")
        
    
    return resul.data[0]
    




        