import os
import uuid
from datetime import datetime, timezone
from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.db.models import Resource, User, Subject, Year, Program
from app.services import authority_service
from app.utils.constants import ALLOWED_RESOURCE_TYPES, MAX_FILE_SIZE
from app.utils.s3 import get_s3_client, get_bucket_name

s3 = get_s3_client()
S3_BUCKET = get_bucket_name()


def _ensure_platform_superadmin(current_user: User):
    if current_user.role != "platform_superadmin":
        raise HTTPException(status_code=403, detail="Only platform superadmin can manage resource approvals")


def validate_resource_type(resource_type: str):
    if resource_type not in ALLOWED_RESOURCE_TYPES:
        raise HTTPException(status_code=400, detail=f"Invalid resource_type. Allowed: {', '.join(ALLOWED_RESOURCE_TYPES)}")

def _can_delete_notes(db: Session, current_user: User, resource: Resource) -> bool:
    if str(resource.uploaded_by) == str(current_user.id):
        return True

    if current_user.role == "platform_superadmin":
        return True

    subject = db.query(Subject).filter(Subject.id == resource.subject_id).first()
    if not subject:
        return False

    year = db.query(Year).filter(Year.id == subject.year_id).first()
    if not year:
        return False

    return (
        authority_service.has_scoped_role(db, current_user, "program_admin", "program", year.program_id)
        or authority_service.has_scoped_role(db, current_user, "college_superadmin", "college", subject.college_id)
    )


def generate_upload_url(db: Session, current_user: User, subject_id: str, resource_type: str, filename: str):
    validate_resource_type(resource_type)

    subject = db.query(Subject).filter(Subject.id == subject_id).first()
    if not subject:
        raise HTTPException(status_code=404, detail="Subject not found")

    if not authority_service.can_manage_subject_resources(
        db,
        current_user,
        subject_id
    ):
        raise HTTPException(status_code=403, detail="Not allowed to upload")

    file_id = str(uuid.uuid4())

    ext = ""
    if filename:
        _, ext = os.path.splitext(filename)

    file_key = f"temp/{current_user.college_id}/{file_id}{ext}"

    presigned_post = s3.generate_presigned_post(
        Bucket=S3_BUCKET,
        Key=file_key,
        Conditions=[["content-length-range", 0, MAX_FILE_SIZE]],
        ExpiresIn=300,
    )

    return {
        "upload_url": presigned_post["url"],
        "fields": presigned_post["fields"],
        "file_key": file_key,
        "max_size_mb": 25,
    }


def confirm_upload(db: Session, current_user: User, subject_id: str, title: str, resource_type: str, file_key: str):
    validate_resource_type(resource_type)

    subject = db.query(Subject).filter(Subject.id == subject_id).first()
    if not subject:
        raise HTTPException(status_code=404, detail="Subject not found")

    if not authority_service.can_manage_subject_resources(
        db,
        current_user,
        subject_id
    ):
        raise HTTPException(status_code=403, detail="Not allowed")

    try:
        s3.head_object(Bucket=S3_BUCKET, Key=file_key)
    except Exception:
        raise HTTPException(status_code=400, detail="File not found")

    permanent_key = file_key.replace("temp/", "permanent/")

    s3.copy_object(
        Bucket=S3_BUCKET,
        CopySource={"Bucket": S3_BUCKET, "Key": file_key},
        Key=permanent_key,
    )

    s3.delete_object(Bucket=S3_BUCKET, Key=file_key)

    new_resource = Resource(
        id=uuid.uuid4(),
        college_id=current_user.college_id,
        subject_id=subject_id,
        title=title,
        resource_type=resource_type,
        approval_status="pending",
        embedding_status="pending",
        file_key=permanent_key,
        uploaded_by=current_user.id,
        is_active=True,
    )

    db.add(new_resource)
    db.commit()
    db.refresh(new_resource)

    return {"message": "Upload confirmed", "resource_id": str(new_resource.id)}


def view_resource(db: Session, current_user: User, resource_id: str):
    resource = db.query(Resource).filter(
        Resource.id == resource_id,
        Resource.is_active == True,
    ).first()

    if not resource:
        raise HTTPException(status_code=404, detail="Resource not found")

    # Only same-college users can view
    if resource.college_id != current_user.college_id:
        raise HTTPException(status_code=403, detail="Access denied")

    if resource.approval_status != "approved":
        raise HTTPException(status_code=403, detail="Resource not approved")

    try:
        s3.head_object(Bucket=S3_BUCKET, Key=resource.file_key)
    except Exception:
        resource.is_active = False
        db.commit()
        raise HTTPException(status_code=404, detail="File no longer exists")

    disposition = "inline" if resource.file_key.lower().endswith(".pdf") else "attachment"

    params = {
        "Bucket": S3_BUCKET,
        "Key": resource.file_key,
        "ResponseContentDisposition": disposition,
    }

    if disposition == "inline":
        params["ResponseContentType"] = "application/pdf"

    view_url = s3.generate_presigned_url(
        "get_object",
        Params=params,
        ExpiresIn=300,
    )
    current_user.resources_viewed_count+=1
    db.query(Resource).filter(Resource.id == resource_id).update(
        {"view_count": Resource.view_count + 1},
        synchronize_session=False
    )
    

    db.commit()
    return {
        "url": view_url,
        "mode": disposition,
        "expires_in_seconds": 300,
    }



def list_resources(db: Session, current_user: User, subject_id: str, resource_type: str):
    validate_resource_type(resource_type)

    resources = (
        db.query(Resource, User.email)
        .join(User, Resource.uploaded_by == User.id)
        .filter(
            Resource.subject_id == subject_id,
            Resource.college_id == current_user.college_id,
            Resource.resource_type == resource_type,
            Resource.approval_status == "approved",
            Resource.is_active == True,
        )
        .order_by(Resource.created_at.desc())
        .all()
    )

    return [
        {
            "id": str(r.Resource.id),
            "title": r.Resource.title,
            "uploaded_by": r.email,
            "created_at": r.Resource.created_at,
            "embedding_status": r.Resource.embedding_status,  
        }
        for r in resources
    ]


def list_platform_resources(db: Session, current_user: User, status: str = "pending"):
    _ensure_platform_superadmin(current_user)

    q = (
        db.query(Resource, User.email)
        .join(User, Resource.uploaded_by == User.id)
        .filter(Resource.is_active == True)
    )

    if status in {"pending", "approved", "rejected"}:
        q = q.filter(Resource.approval_status == status)

    resources = q.order_by(Resource.created_at.desc()).all()

    return [
        {
            "id": str(r.Resource.id),
            "title": r.Resource.title,
            "subject_id": str(r.Resource.subject_id),
            "resource_type": r.Resource.resource_type,
            "uploaded_by": r.email,
            "created_at": r.Resource.created_at,
            "approval_status": r.Resource.approval_status,
            "rejection_reason": r.Resource.rejection_reason,
        }
        for r in resources
    ]


def preview_resource(db: Session, current_user: User, resource_id: str):
    _ensure_platform_superadmin(current_user)

    resource = db.query(Resource).filter(
        Resource.id == resource_id,
        Resource.is_active == True,
    ).first()

    if not resource:
        raise HTTPException(status_code=404, detail="Resource not found")

    try:
        s3.head_object(Bucket=S3_BUCKET, Key=resource.file_key)
    except Exception:
        resource.is_active = False
        db.commit()
        raise HTTPException(status_code=404, detail="File no longer exists")

    signed_url = s3.generate_presigned_url(
        "get_object",
        Params={
            "Bucket": S3_BUCKET,
            "Key": resource.file_key,
        },
        ExpiresIn=300,
    )

    return {"preview_url": signed_url}


def approve_resource(db: Session, current_user: User, resource_id: str):
    _ensure_platform_superadmin(current_user)

    resource = db.query(Resource).filter(
        Resource.id == resource_id,
        Resource.is_active == True,
    ).first()

    if not resource:
        raise HTTPException(status_code=404, detail="Resource not found")

    resource.approval_status = "approved"
    resource.approved_by = current_user.id
    resource.approved_at = datetime.now(timezone.utc)
    resource.rejection_reason = None

    db.commit()
    db.refresh(resource)

    return {
        "message": "Resource approved",
        "resource_id": str(resource.id),
        "approval_status": resource.approval_status,
    }


def reject_resource(db: Session, current_user: User, resource_id: str, rejection_reason: str):
    _ensure_platform_superadmin(current_user)

    resource = db.query(Resource).filter(
        Resource.id == resource_id,
        Resource.is_active == True,
    ).first()

    if not resource:
        raise HTTPException(status_code=404, detail="Resource not found")

    resource.approval_status = "rejected"
    resource.rejection_reason = rejection_reason
    resource.approved_by = None
    resource.approved_at = None

    db.commit()
    db.refresh(resource)

    return {
        "message": "Resource rejected",
        "resource_id": str(resource.id),
        "approval_status": resource.approval_status,
    }


def delete_resource(db: Session, current_user: User, resource_id: str):

    resource = db.query(Resource).filter(
        Resource.id == resource_id
    ).first()

    if not resource:
        raise HTTPException(status_code=404, detail="Resource not found")

    if resource.college_id != current_user.college_id:
        raise HTTPException(status_code=403, detail="Access denied")

    if resource.resource_type == "notes":
        if not _can_delete_notes(db, current_user, resource):
            raise HTTPException(
                status_code=403,
                detail="Only the owner or program admin and above can delete notes",
            )
    else:
        if not authority_service.can_manage_subject_resources(
            db,
            current_user,
            resource.subject_id
        ):
            raise HTTPException(status_code=403, detail="Not allowed")

    try:
        from app.db.models.resource_embedding import ResourceEmbedding

        db.query(ResourceEmbedding).filter(
            ResourceEmbedding.resource_id == resource_id
        ).delete(synchronize_session=False)


        try:
            s3.delete_object(Bucket=S3_BUCKET, Key=resource.file_key)
        except Exception:
            pass


        db.delete(resource)

        db.commit()

        return {"message": "Resource permanently deleted"}

    except Exception:
        db.rollback()
        raise
