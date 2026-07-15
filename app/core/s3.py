"""
Storage abstraction: S3-compatible (MinIO/AWS) + local filesystem fallback for dev.
Handles: profile photos, message media, with CDN url generation.
Designed for 10M daily media uploads.
"""
import os
import uuid
import shutil
from pathlib import Path
from typing import BinaryIO, Optional
from functools import lru_cache

from .config import settings

try:
    import boto3
    from botocore.exceptions import ClientError
    _boto_available = True
except ImportError:
    _boto_available = False

LOCAL_MEDIA_ROOT = Path("./storage")
LOCAL_MEDIA_ROOT.mkdir(exist_ok=True)
(LOCAL_MEDIA_ROOT / "profile").mkdir(exist_ok=True)
(LOCAL_MEDIA_ROOT / "message").mkdir(exist_ok=True)

class StorageService:
    def __init__(self):
        self.s3_client = None
        self.use_s3 = False
        if _boto_available and settings.S3_ENDPOINT_URL:
            try:
                self.s3_client = boto3.client(
                    "s3",
                    endpoint_url=settings.S3_ENDPOINT_URL,
                    aws_access_key_id=settings.S3_ACCESS_KEY,
                    aws_secret_access_key=settings.S3_SECRET_KEY,
                    region_name=settings.S3_REGION,
                )
                # try ensure buckets
                for bucket in [settings.S3_BUCKET_MEDIA, settings.S3_BUCKET_MESSAGE_MEDIA]:
                    try:
                        self.s3_client.head_bucket(Bucket=bucket)
                    except:
                        try:
                            self.s3_client.create_bucket(Bucket=bucket)
                        except Exception:
                            pass
                self.use_s3 = True
            except Exception:
                self.use_s3 = False
        elif _boto_available and not settings.S3_ENDPOINT_URL:
            # Try AWS without endpoint (real S3)
            try:
                self.s3_client = boto3.client(
                    "s3",
                    aws_access_key_id=settings.S3_ACCESS_KEY,
                    aws_secret_access_key=settings.S3_SECRET_KEY,
                    region_name=settings.S3_REGION,
                )
                self.use_s3 = True
            except Exception:
                self.use_s3 = False

    def _s3_key(self, folder: str, filename: str) -> str:
        return f"{folder}/{filename}"

    def save(self, file_obj: BinaryIO, folder: str = "profile", content_type: str = "image/jpeg") -> tuple[str, str]:
        """
        Returns (storage_key, public_url)
        """
        ext = ".jpg"
        # try guess ext from content_type
        if "png" in content_type:
            ext = ".png"
        elif "webp" in content_type:
            ext = ".webp"
        elif "mp4" in content_type:
            ext = ".mp4"
        filename = f"{uuid.uuid4().hex}{ext}"
        key = self._s3_key(folder, filename)

        # read bytes
        file_obj.seek(0)
        data = file_obj.read()

        if self.use_s3 and self.s3_client:
            bucket = settings.S3_BUCKET_MEDIA if folder == "profile" else settings.S3_BUCKET_MESSAGE_MEDIA
            try:
                self.s3_client.put_object(
                    Bucket=bucket,
                    Key=key,
                    Body=data,
                    ContentType=content_type,
                )
                public_url = f"{settings.MEDIA_CDN_URL.rstrip('/')}/{key}" if folder == "profile" else f"{settings.S3_ENDPOINT_URL}/{bucket}/{key}"
                return key, public_url
            except Exception as e:
                # fallback to local
                pass

        # Local filesystem fallback
        local_path = LOCAL_MEDIA_ROOT / key
        local_path.parent.mkdir(parents=True, exist_ok=True)
        with open(local_path, "wb") as f:
            f.write(data)
        public_url = f"/storage/{key}"  # served via FastAPI static
        return key, public_url

    def delete(self, storage_key: str, folder: str = "profile"):
        if self.use_s3 and self.s3_client:
            bucket = settings.S3_BUCKET_MEDIA if folder == "profile" else settings.S3_BUCKET_MESSAGE_MEDIA
            try:
                self.s3_client.delete_object(Bucket=bucket, Key=storage_key)
                return True
            except Exception:
                pass
        try:
            local_path = LOCAL_MEDIA_ROOT / storage_key
            if local_path.exists():
                local_path.unlink()
            return True
        except Exception:
            return False

    def generate_presigned_url(self, storage_key: str, folder: str = "profile", expires=3600) -> Optional[str]:
        if self.use_s3 and self.s3_client:
            bucket = settings.S3_BUCKET_MEDIA if folder == "profile" else settings.S3_BUCKET_MESSAGE_MEDIA
            try:
                return self.s3_client.generate_presigned_url(
                    "get_object",
                    Params={"Bucket": bucket, "Key": storage_key},
                    ExpiresIn=expires,
                )
            except Exception:
                return None
        return f"/storage/{storage_key}"

@lru_cache()
def get_storage() -> StorageService:
    return StorageService()
