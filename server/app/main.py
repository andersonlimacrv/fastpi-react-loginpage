import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import db
from app.service.auth_service import generate_role

def init_app():
    db.init()

    app = FastAPI(
        title="Login App",  
        description="Login Page",
        version="1.0.0"
    )
    
    @app.on_event("startup")
    async def startup():
        await db.create_all()
        await generate_role()

    @app.on_event("shutdown")
    async def shutdown():
        await db.close()

    from app.controller import authentication, users

    app.include_router(authentication.router)
    app.include_router(users.router)

    return app

app = init_app()

def start():
    """Launched with 'poetry run start' at root level."""
    uvicorn.run("app.main:app", host="localhost", port=8888, reload=True)
