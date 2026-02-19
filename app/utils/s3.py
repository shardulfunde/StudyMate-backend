from app.core.config import s3_client, S3_BUCKET


def get_s3_client():
    return s3_client


def get_bucket_name():
    return S3_BUCKET
