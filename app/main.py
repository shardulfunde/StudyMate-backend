from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1 import core, resources, admin, catalog, moderator
from app.core import config
from app.api.v1 import me  
from app.api.v1 import create_embedding
from app.api.v1 import ai_test   # whatever you named the file
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from fastapi.responses import JSONResponse
from fastapi import Request
from app.core.limiter import limiter

app = FastAPI()

app.state.limiter = limiter

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:5174",# local dev
        "https://www.studymateai.tech",
        "https://studymateai.tech",
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)


app.add_middleware(SlowAPIMiddleware)

@app.exception_handler(RateLimitExceeded)
def rate_limit_handler(request, exc):
    return JSONResponse(
        status_code=429,
        content={"detail": "Rate limit exceeded. Try again later."},
    )

app.include_router(core.router)
app.include_router(resources.router)
app.include_router(admin.router)
app.include_router(catalog.router)
app.include_router(moderator.router)
app.include_router(me.router)
app.include_router(create_embedding.router) 
app.include_router(ai_test.router)
