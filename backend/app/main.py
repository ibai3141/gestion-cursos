from fastapi import FastAPI
from app.routes import auth


app = FastAPI()



app.include_router(auth.router)

@app.get("/")
def root():
    return{"mensaje": "funciona"}