from fastapi import FastAPI
from app.routes import auth, cursos, inscripciones,profesores


app = FastAPI()



app.include_router(auth.router)
app.include_router(cursos.router)
app.include_router(inscripciones.router)
app.include_router(profesores.router)


@app.get("/")
def root():
    return{"mensaje": "funciona"}