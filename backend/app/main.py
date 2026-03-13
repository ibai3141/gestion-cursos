from fastapi import FastAPI
from app.routes import auth, cursos


app = FastAPI()



app.include_router(auth.router)
app.include_router(cursos.router)

@app.get("/")
def root():
    return{"mensaje": "funciona"}