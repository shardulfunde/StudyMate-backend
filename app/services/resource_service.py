import os
import uuid
from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.db.models import Resource, User, Subject, Year, Program
from app.services import authority_service
from app.utils.constants import ALLOWED_RESOURCE_TYPES, MAX_FILE_SIZE
from app.utils.s3 import get_s3_client, get_bucket_name

s3 = get_s3_client()
S3_BUCKET = get_bucket_name()


def validate_resource_type(resource_type: str):
    if resource_type not in ALLOWED_RESOURCE_TYPES:
        raise HTTPException(status_code=400, detail=f"Invalid resource_type. Allowed: {', '.join(ALLOWED_RESOURCE_TYPES)}")


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

def delete_resource(db: Session, current_user: User, resource_id: str):

    resource = db.query(Resource).filter(
        Resource.id == resource_id
    ).first()

    if not resource:
        raise HTTPException(status_code=404, detail="Resource not found")

    if resource.college_id != current_user.college_id:
        raise HTTPException(status_code=403, detail="Access denied")

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
