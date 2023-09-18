import uvicorn 
from fastapi import FastAPI, APIRouter
from app.config import db

def init_app():
    db.init()

    app = FastAPI(
        tittle= "Login App",
        description="Login Page",
        version="1.0.0"
    )

    @app.on_event("startup")
    async def startup():
        await db.create_all()

    @app.on_event("shutdown")
    async def shutdown():
        await db.close()

    return app

app = init_app()

def start():
    """Launched with 'poetry run start' at root level."""
    uvicorn.run("app.main:app", host="localhost", port=8888, reload=True)