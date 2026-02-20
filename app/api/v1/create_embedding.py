from app.tasks.embedding import generate_embeddings
from fastapi import APIRouter, HTTPException, status, Depends
from app.core.deps import get_db, get_current_user
from app.db.models.resource import Resource
from sqlalchemy.orm import Session
from app.db.models.user import User
from app.services.authority_service import can_manage_subject_resources
from app.core.limiter import limiter
from fastapi import Request
router = APIRouter()

@router.post("/resources/{resource_id}/generate_embeddings")
@limiter.limit("5/minute")
def create_embeddings(
    request:Request,
    resource_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    resource_obj = db.query(Resource).filter(Resource.id == resource_id).first()
    if not resource_obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resource not found")

    if not can_manage_subject_resources(db, current_user, resource_obj.subject_id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to manage resources for this subject")

    if resource_obj.embedding_status == "completed":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Embeddings already generated for this resource")

    if resource_obj.embedding_status == "processing":
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Embedding generation already in progress")
    
    generate_embeddings.delay(str(resource_obj.id))

    return {"message": "Embedding generation started"}
