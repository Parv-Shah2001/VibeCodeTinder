"""
Media processing pipeline designed for 10M daily uploads.
Steps:
1. Validate mime type + size
2. Virus scan placeholder
3. Resize / thumbnails via Pillow
4. NSFW moderation placeholder (would call AWS Rekognition / internal model)
5. Store to S3 / local
"""
from PIL import Image
import io
import os
from typing import Tuple

MAX_SIZE_MB = 20
ALLOWED_TYPES = {"image/jpeg", "image/png", "image/webp", "image/jpg"}

def validate_file(content_type: str, size_bytes: int):
    if content_type not in ALLOWED_TYPES and not content_type.startswith("video/"):
        raise ValueError(f"Unsupported content type {content_type}")
    if size_bytes > MAX_SIZE_MB * 1024 * 1024:
        raise ValueError(f"File too large, max {MAX_SIZE_MB} MB")

def process_image(image_bytes: bytes) -> Tuple[bytes, bytes, Tuple[int, int]]:
    """
    Returns (processed_image_bytes, thumbnail_bytes, (width, height))
    """
    try:
        img = Image.open(io.BytesIO(image_bytes))
        if img.mode in ("RGBA", "LA"):
            background = Image.new("RGB", img.size, (255, 255, 255))
            background.paste(img, mask=img.split()[-1])
            img = background
        else:
            img = img.convert("RGB")

        w, h = img.size

        # Resize max 1080px for main
        max_side = 1080
        if max(w, h) > max_side:
            if w > h:
                new_w = max_side
                new_h = int(h * max_side / w)
            else:
                new_h = max_side
                new_w = int(w * max_side / h)
            img_resized = img.resize((new_w, new_h), Image.LANCZOS)
        else:
            img_resized = img

        # Thumbnail 300x400 cover-like
        thumb = img.copy()
        thumb.thumbnail((300, 400), Image.LANCZOS)

        main_buf = io.BytesIO()
        img_resized.save(main_buf, format="JPEG", quality=85, optimize=True)

        thumb_buf = io.BytesIO()
        thumb.save(thumb_buf, format="JPEG", quality=70, optimize=True)

        return main_buf.getvalue(), thumb_buf.getvalue(), (w, h)
    except Exception as e:
        raise ValueError(f"Image processing failed: {str(e)}")

def mock_nsfw_check(image_bytes: bytes) -> Tuple[bool, float]:
    """
    Placeholder NSFW moderation.
    Production would call:
      - AWS Rekognition DetectModerationLabels
      - Custom TensorFlow/PyTorch model for nudity
    Returns (is_nsfw, score)
    """
    # Naive: if image mostly red-ish? For demo always safe.
    return False, 0.01

def mock_virus_scan(image_bytes: bytes) -> bool:
    # Placeholder for ClamAV / commercial AV
    return True
