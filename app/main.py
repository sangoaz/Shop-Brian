from fastapi import FastAPI
from sqlmodel import SQLModel
from contextlib import asynccontextmanager

from app.core.database import engine
from app import models

#from app.routes.clothes import router as clothes_router
from app.routes.admin.admin_collections import router as admin_collections_router
from app.routes.auth import router as auth_router
from app.routes.admin.admin_clothes import router as admin_clothes_router
from app.routes.public.public_clothes import router as public_clothes_router
from app.routes.public.public_clothes_in_collection import router as public_clothes_in_collection
from app.routes.public.public_collections import router as public_collections_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    # SQLModel.metadata.create_all(engine)
    yield

app = FastAPI(lifespan=lifespan)

"""
# Branchement du dossier des photos uploadés
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://glf-auto.vercel.app",
    ],
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)
"""

# Branchement des différentes routes du dossier routes
#app.include_router(clothes_router)
app.include_router(admin_collections_router)
app.include_router(admin_clothes_router)
app.include_router(auth_router)
app.include_router(public_collections_router)
app.include_router(public_clothes_router)
app.include_router(public_clothes_in_collection)

