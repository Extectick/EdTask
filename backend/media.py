import io
import json
import os
import time
import uuid
from urllib.parse import urlparse

from minio import Minio
from minio.error import S3Error


_minio_client = None


def _get_required_env(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        raise RuntimeError(f"{name} is required for MinIO image storage.")
    return value


def _get_bool_env(name: str, default: str = "false") -> bool:
    return os.getenv(name, default).strip().lower() in {"1", "true", "yes", "on"}


def get_minio_client() -> Minio:
    global _minio_client
    if _minio_client is None:
        _minio_client = Minio(
            _get_required_env("MINIO_ENDPOINT"),
            access_key=_get_required_env("MINIO_ACCESS_KEY"),
            secret_key=_get_required_env("MINIO_SECRET_KEY"),
            secure=_get_bool_env("MINIO_SECURE"),
        )
    return _minio_client


def get_minio_bucket() -> str:
    return _get_required_env("MINIO_BUCKET")


def get_minio_public_url() -> str:
    return _get_required_env("MINIO_PUBLIC_URL").rstrip("/")


def get_backend_public_url() -> str:
    return os.getenv("BACKEND_PUBLIC_URL", "http://localhost:8000").rstrip("/")


def build_image_url(object_name: str) -> str:
    return f"{get_minio_public_url()}/{get_minio_bucket()}/{object_name.lstrip('/')}"


def build_legacy_image_url(path: str) -> str:
    normalized_path = path.replace("\\", "/").lstrip("/")
    return f"{get_backend_public_url()}/{normalized_path}"


def extract_image_name(image_url: str) -> str:
    return urlparse(image_url).path.rstrip("/").split("/")[-1]


def extract_object_name(image_url: str) -> str:
    path = urlparse(image_url).path.lstrip("/")
    bucket_prefix = f"{get_minio_bucket()}/"
    if path.startswith(bucket_prefix):
        return path[len(bucket_prefix):]
    return path


def ensure_image_bucket() -> None:
    client = get_minio_client()
    bucket = get_minio_bucket()
    last_error = None

    for _ in range(10):
        try:
            if not client.bucket_exists(bucket):
                client.make_bucket(bucket)

            policy = {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Principal": {"AWS": ["*"]},
                        "Action": ["s3:GetObject"],
                        "Resource": [f"arn:aws:s3:::{bucket}/*"],
                    }
                ],
            }
            client.set_bucket_policy(bucket, json.dumps(policy))
            return
        except Exception as exc:
            last_error = exc
            time.sleep(2)

    raise RuntimeError("Failed to initialize MinIO bucket for images.") from last_error


def upload_image(content: bytes, original_filename: str, content_type: str) -> tuple[str, str]:
    extension = os.path.splitext(original_filename or "")[1]
    object_name = f"images/{uuid.uuid4()}{extension}"
    client = get_minio_client()
    bucket = get_minio_bucket()
    client.put_object(
        bucket,
        object_name,
        io.BytesIO(content),
        length=len(content),
        content_type=content_type,
    )
    return object_name, build_image_url(object_name)


def delete_image(image_url: str) -> None:
    if not image_url:
        return

    if not image_url.startswith(("http://", "https://")):
        if os.path.exists(image_url):
            os.remove(image_url)
        return

    client = get_minio_client()
    bucket = get_minio_bucket()
    object_name = extract_object_name(image_url)

    try:
        client.remove_object(bucket, object_name)
    except S3Error as exc:
        if exc.code not in {"NoSuchKey", "NoSuchObject", "NoSuchBucket"}:
            raise


def serialize_image(image) -> dict | None:
    if not image or not image.path:
        return None

    image_url = image.path if image.path.startswith(("http://", "https://")) else build_legacy_image_url(image.path)

    return {
        "id": image.id,
        "image_name": extract_image_name(image_url),
        "image_url": image_url,
    }
