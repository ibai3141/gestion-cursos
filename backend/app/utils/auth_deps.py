from typing import Annotated
from fastapi import Depends, HTTPException, status
import supabase
from supabase_auth import User
from app.config import settings
import bcrypt 
from jose import jwt
from datetime import datetime, timedelta, timezone
from fastapi.security import OAuth2PasswordBearer

#firmar el token
secret_key = settings.SECRET_KEY
algoritmo = settings.ALGORITHM
access_tokken_expire = settings.ACCESS_TOKEN_EXPIRE_MINUTES


# Metodo para hashear la contraseña
# recibe una contraseña str y devuelve el hash en str para almecenarlo en la base de datos
def get_password_hash(password: str) -> str:
    
    #combierte a bytes las contraseña porque hashpw recibe bytes
    password_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    
    hashed_str = bcrypt.hashpw(password_bytes, salt)
    
    #devolvemos las contraseña como str
    return hashed_str.decode('utf-8')
    
    
# metodo para verificar la contraseña 
# recibe la contraseña y la contraseña hash de la bd y comprueba si es verdadera o falsa
def verify_password(plain_password: str, hashed_password: str) -> bool:
    
    status = False
    
    #pasamos a bytes las contraseñas porque chechkpw recibe bytes como argumentos
    plain_bytes = plain_password.encode('utf-8')
    hashed_bytes = hashed_password.encode('utf-8')

    
    if bcrypt.checkpw(plain_bytes, hashed_bytes):
        status = True
        
    return status

# Funciones de JWT

# metodo para crear un tokken 
def create_access_tokken(data : dict) -> str:
    
    #se crea la expiracion del tokken
    expire = datetime.now(timezone.utc) + timedelta(minutes=access_tokken_expire)
    #se añade el tiempo al dict con la informacion recibida
    #{'datos': 'ejemlo', 'exp': 1773303911}
    data.update({"exp": expire})
    
    #se firma el tokken y se devuelve
    tokken = jwt.encode(data, secret_key, algoritmo)
    
    return tokken

#metodo para verificar el tokken y decodificarlo
def verify_tokken( tokken: str)-> dict:
    
    # verifica si la firma del tokken es la correcta y devuelve el dict con la iformacion si es la correcta
    result = jwt.decode(tokken, secret_key, algoritmo)
    
    return result
    

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


# Dependencias de usuario
async def get_current_user(token: str = Depends(oauth2_scheme)):
    # 1. Verificar el token
    payload = verify_tokken(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    # 2. Extraer ID y rol del token
    user_id = payload.get("sub")
    rol = payload.get("rol")  # ← Esto viene del token, no de BD
    
    if not user_id or not rol:
        raise HTTPException(status_code=401, detail="Invalid token data")
    
    # 3. Buscar en la tabla correspondiente según el rol del token
    try:
        if rol == "profesor":
            response = supabase.table("profesores").select("*").eq("id", user_id).execute()
        elif rol == "estudiante":
            response = supabase.table("estudiantes").select("*").eq("id", user_id).execute()
        else:
            raise HTTPException(status_code=401, detail="Invalid role")
        
        if not response.data:
            raise HTTPException(status_code=401, detail="User not found")
        
        # Añadir el rol al objeto usuario (útil para endpoints)
        usuario = response.data[0]
        usuario["rol"] = rol  # ← Añades el rol al resultado
        
        return usuario
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    


