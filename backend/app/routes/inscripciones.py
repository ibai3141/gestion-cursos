'''
POST	/inscripciones/	Estudiante se inscribe en un curso	
DELETE	/inscripciones/{id}	Estudiante cancela su inscripción	
PUT	/inscripciones/{id}	Profesor pone calificación
GET	/inscripciones/mis-cursos	Ver cursos del estudiante con calificaciones	
'''
from fastapi import APIRouter, HTTPException, Depends
from app.utils import auth_deps
from app.database import supabase
from app.models import inscripcion  


router = APIRouter(prefix="/inscripciones", tags=["inscripciones"])


@router.post("/", response_model=inscripcion.InscripcionResponse)
async def altaInscripcion(inscripcion_data : inscripcion.InscripcionCreate, usuario = Depends(auth_deps.get_current_user)):
    
    if usuario["rol"] == "estudiante":
        result = supabase.table("inscripciones").insert({
            "estudiante_id": usuario["sub"],
            "curso_id": inscripcion_data.curso_id
        }).execute()
    else:
        raise HTTPException(status_code=403, detail="Solo los estudiantes pueden inscribirse")

    return result.data[0]
