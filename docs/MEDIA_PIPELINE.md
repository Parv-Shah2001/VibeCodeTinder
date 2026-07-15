# Media Pipeline

Target: 10M uploads/day (115/sec avg, ~345 peak)

## Flow

1. **Client Upload**
   - Profile photo: `POST /media/me/upload` multipart.
   - Message media: `POST /media/messages/{id}/upload`
   - Frontend shows optimistic UI + progress.

2. **Validation (processor.py)**
   - MIME allowlist: image/jpeg, png, webp, video/mp4 (for messages)
   - Size limit: 20MB via settings
   - Virus scan placeholder `mock_virus_scan` -> production would call ClamAV daemon or commercial scanner.

3. **Image Processing**
   - Pillow:
     - Convert RGBA -> RGB white background
     - Main image resize longest side 1080px, quality 85, optimize.
     - Thumbnail 300x400 (thumbnail method).
   - Returns (main_bytes, thumb_bytes, (w,h))

4. **Moderation**
   - `mock_nsfw_check` -> placeholder for AWS Rekognition DetectModerationLabels or custom model.
   - Returns (is_nsfw, score). If NSFW -> 400 content policy.

5. **Storage Abstraction (s3.py)**
   - Detects S3 config: if `S3_ENDPOINT_URL` set (MinIO) or credentials for AWS.
   - Tries S3 put_object with content-type.
   - Fallback to local filesystem `./storage/{folder}/{uuid}.jpg` for dev.
   - Generates public_url: CDN URL if configured else presigned or `/storage/...` local.

6. **DB Metadata**
   - `media_assets` row: storage_key, public_url, thumbnail_url, dimensions, size_bytes, moderation_score.
   - `is_primary` true if first photo.
   - `display_order` for user sorting.

7. **Event**
   - Publishes `MEDIA_UPLOADED` -> could trigger further async jobs (face detection, embedding).

## Scale Improvements

- **Async Worker**: Replace sync processing with Celery + Redis broker + S3. Upload raw file to `incoming/` bucket, enqueue job `process_media(asset_id)`. Worker does steps 2-5.
- **Multipart**: For video >100MB use S3 multipart upload + presigned POST from client direct to S3 to avoid API server bandwidth (10M *2MB=20TB/day through API would need 2.3 Gbps constant). Direct upload pattern: backend returns presigned URL, client uploads direct, then notifies backend.
- **CDN**: CloudFront with origin S3. Cache-Control public,max-age=31536000. Invalidation on delete.
- **Dedup**: Hash file SHA256, check existing assets to avoid duplicate storage.
- **Cold storage**: After 90 days of profile deletion, move to Glacier.

## Message Media

Same flow but:
- Allows video
- Stored in separate bucket `vibe-message-media`
- Thumbnail only for images
- Linked via `media_asset_id` in messages table.

## Security

- Presigned URL expiry 3600s for private buckets.
- Content-Type enforced, no SVG to avoid XSS.
- Virus scan before storage.
- Rate limiting per user.

## Monitoring

- Metrics: upload_duration_histogram, upload_bytes_counter, moderation_score_histogram.
- Alerts if NSFW rate > 5% or processing p95 >1s.

