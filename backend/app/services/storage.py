"""MinIO/S3 storage client for report PDFs and assets."""
import io

import boto3
from botocore.client import Config

from app.config import settings

_client = None


def _get_client():
    global _client
    if _client is None:
        _client = boto3.client(
            "s3",
            endpoint_url=f"{'https' if settings.MINIO_SECURE else 'http'}://{settings.MINIO_ENDPOINT}",
            aws_access_key_id=settings.MINIO_ACCESS_KEY,
            aws_secret_access_key=settings.MINIO_SECRET_KEY,
            config=Config(signature_version="s3v4"),
            region_name="us-east-1",
        )
        # Ensure bucket exists
        try:
            _client.head_bucket(Bucket=settings.MINIO_BUCKET)
        except Exception:
            _client.create_bucket(Bucket=settings.MINIO_BUCKET)
    return _client


def upload_pdf(key: str, pdf_bytes: bytes) -> str:
    client = _get_client()
    client.put_object(
        Bucket=settings.MINIO_BUCKET,
        Key=key,
        Body=io.BytesIO(pdf_bytes),
        ContentType="application/pdf",
    )
    return f"{settings.MINIO_ENDPOINT}/{settings.MINIO_BUCKET}/{key}"


def get_presigned_url(key: str, expires: int = 3600) -> str:
    client = _get_client()
    return client.generate_presigned_url(
        "get_object",
        Params={"Bucket": settings.MINIO_BUCKET, "Key": key},
        ExpiresIn=expires,
    )
