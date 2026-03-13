from fastapi import FastAPI
from app.routes import auth, cursos, inscripciones


app = FastAPI()



app.include_router(auth.router)
app.include_router(cursos.router)
app.include_router(inscripciones.router)

@app.get("/")
def root():
    return{"mensaje": "funciona"}