from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer
from firebase_admin import auth as firebase_auth
from app.core import config
from fastapi import Request

security = HTTPBearer()


def verify_token(request: Request, credentials=Depends(security)):
    token = credentials.credentials

    try:
        decoded_token = firebase_auth.verify_id_token(token)
        
        request.state.uid = decoded_token["uid"]

        return decoded_token
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired Firebase token"
        )
