from slowapi import Limiter
from slowapi.util import get_remote_address
from fastapi import Request

def user_key_func(request: Request):
    return getattr(request.state, "uid", get_remote_address(request))

limiter = Limiter(key_func=user_key_func)