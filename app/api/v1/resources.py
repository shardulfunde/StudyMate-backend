from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.deps import get_db, get_current_user
from app.db.models import User
from app.schemas import ResourceRejectRequest
from app.services import resource_service

router = APIRouter()


@router.post("/generate-upload-url/{subject_id}/{resource_type}")
def generate_upload_url(
    subject_id: str,
    resource_type: str,
    filename: str = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return resource_service.generate_upload_url(db, current_user, subject_id, resource_type, filename)


@router.post("/confirm-upload")
def confirm_upload(
    subject_id: str,
    title: str,
    resource_type: str,
    file_key: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return resource_service.confirm_upload(db, current_user, subject_id, title, resource_type, file_key)


@router.get("/view/{resource_id}")
def view_resource(
    resource_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return resource_service.view_resource(db, current_user, resource_id)


@router.get("/resources/{subject_id}/{resource_type}")
def list_resources(
    subject_id: str,
    resource_type: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return resource_service.list_resources(db, current_user, subject_id, resource_type)


@router.get("/platform/resources")
def list_platform_resources(
    status: str = "pending",
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return resource_service.list_platform_resources(db, current_user, status)


@router.get("/platform/resources/{resource_id}/preview")
def preview_resource(
    resource_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return resource_service.preview_resource(db, current_user, resource_id)


@router.patch("/platform/resources/{resource_id}/approve")
def approve_resource(
    resource_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return resource_service.approve_resource(db, current_user, resource_id)


@router.patch("/platform/resources/{resource_id}/reject")
def reject_resource(
    resource_id: str,
    request: ResourceRejectRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return resource_service.reject_resource(db, current_user, resource_id, request.rejection_reason)


@router.delete("/resource/{resource_id}")
def delete_resource(
    resource_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return resource_service.delete_resource(db, current_user, resource_id)
