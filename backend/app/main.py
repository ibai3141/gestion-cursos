from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import auth, cursos, inscripciones, profesores, microsoft_auth


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



app.include_router(auth.router)
app.include_router(microsoft_auth.router)
app.include_router(cursos.router)
app.include_router(inscripciones.router)
app.include_router(profesores.router)


@app.get("/")
def root():
    return{"mensaje": "funciona"}
