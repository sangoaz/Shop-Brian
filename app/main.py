from fastapi import FastAPI
from sqlmodel import SQLModel
from contextlib import asynccontextmanager

from app.core.database import engine
from app import models

from app.routes.admin.admin_collections import router as admin_collections_router
from app.routes.auth import router as auth_router
from app.routes.admin.admin_product import router as admin_product_router
from app.routes.admin.admin_product_variant import router as admin_product_variant_router
from app.routes.public.public_product import router as public_product_router
from app.routes.public.public_products_in_collection import router as public_product_in_collection
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
# Routes admin
app.include_router(admin_collections_router)
app.include_router(admin_product_router)
app.include_router(admin_product_variant_router)

# Routes d'utilisateur
app.include_router(auth_router)

# Routes publiques
app.include_router(public_collections_router)
app.include_router(public_product_router)
app.include_router(public_product_in_collection)

