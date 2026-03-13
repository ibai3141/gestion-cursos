'''
POST /auth/registro/profesor   → Crear un nuevo profesor
POST /auth/registro/estudiante → Crear un nuevo estudiante
POST /auth/login               → Verificar credenciales y devolver token
'''
from app.utils import auth_deps
from fastapi import APIRouter, HTTPException
from app.database import supabase
from app.models import estudiante, profesor


router = APIRouter(prefix="/auth", tags=["autenticación"])

@router.post("/registro/profesor", response_model=profesor.ProfesorResponse)
async def altaProfesor(profesor_data: profesor.ProfesorCreate):
    
    # 1. Verificar si el email ya existe
    existing = supabase.table("profesores").select("*").eq("email", profesor_data.email).execute()
    if existing.data:
        raise HTTPException(status_code=400, detail="Email ya registrado")
    
    try:
        resultado = supabase.table("profesores").insert([{
            "nombre": profesor_data.nombre,
            "email": profesor_data.email,
            "password_hash": auth_deps.get_password_hash(profesor_data.password)
        }]).execute()
        
        
        return resultado.data[0]
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    
@router.post("/registro/estudiante", response_model=estudiante.EstudianteResponse)
async def altaAlumno(estudiante_data: estudiante.EstudianteCreate):
    
    # 1. Verificar si el email ya existe
    existing = supabase.table("estudiantes").select("*").eq("email", estudiante_data.email).execute()
    if existing.data:
        raise HTTPException(status_code=400, detail="Email ya registrado")
    
    try:
        resultado = supabase.table("estudiantes").insert([{
            "nombre": estudiante_data.nombre,
            "email": estudiante_data.email,
            "password_hash": auth_deps.get_password_hash(estudiante_data.password)
        }]).execute()
        
        
        return resultado.data[0]
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/login")
async def login(email: str, contrasenia:str):
    
    # Buscar en profesores
    profe = supabase.table("profesores").select("*").eq("email", email).execute()
    
    if profe.data:
        usuario = profe.data[0]
        rol = "profesor"

    else:# Buscar en estudiantes
        est = supabase.table("estudiantes").select("*").eq("email", email).execute()
        
        if est.data:
            usuario = est.data[0]
            rol = "estudiante"
        else:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        
    if not auth_deps.verify_password(contrasenia, usuario["password_hash"]):
        raise HTTPException(status_code=401, detail="Password incorrecto")
    
    token_data = {"sub": str(usuario["id"]), "rol": rol}  # ← Convertir a string
    token = auth_deps.create_access_tokken(token_data)
    
    return {"access_token": token, "token_type": "bearer", "rol": rol}

