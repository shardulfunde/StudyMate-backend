from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1 import core, resources, admin, catalog
from app.core import config
from app.api.v1 import me  
from app.api.v1 import create_embedding
from app.api.v1 import ai_test   # whatever you named the file




app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(core.router)
app.include_router(resources.router)
app.include_router(admin.router)
app.include_router(catalog.router)
app.include_router(me.router)
app.include_router(create_embedding.router) 
app.include_router(ai_test.router)