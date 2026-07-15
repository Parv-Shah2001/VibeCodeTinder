# Security – Production Hardening for 50M Users

## Auth
- Bcrypt with cost 12
- JWT access 60min, refresh 30 days rotation
- Refresh token stored httpOnly cookie in production (XSS mitigation) – frontend currently uses localStorage for simplicity, should move to cookies + CSRF
- Password strength validation min 8 chars

## Rate Limiting
- Global middleware 300 req/min/IP (in-memory fallback, Redis in prod)
- Swipe 100/min per user via Redis INCR window
- Message 60/min per user
- Upload limits 20MB

## Content Moderation
- Media pipeline: virus scan (ClamAV placeholder), NSFW detection (Rekognition placeholder) – blocks on is_nsfw true
- Report & Block: blocked users filtered in discovery (geo query excludes blocked ids) and messaging (ensure_conversation_access checks block)
- Text moderation: would add Perspective API for toxic content

## Data Privacy
- Profile `show_me` toggle hides from discovery
- Block prevents any interaction
- GDPR: user deletion cascades all models (profiles, media, swipes, matches, messages) via `ondelete=CASCADE`
- Media S3 presigned URLs expire 3600s, CDN cache-control private for sensitive
- No email/phone leakage in public endpoints

## Infrastructure
- CORS restricted in prod to frontend domain
- Nginx security headers: X-Frame-Options SAMEORIGIN, X-Content-Type nosniff, XSS block
- Secrets in k8s Secret + env, not committed
- DB password strong, RDS encryption at rest
- S3 buckets private, CloudFront OAC

## Monitoring for Abuse
- Analytics events track swipe velocity – if user swipes >1000/min flag bot
- Message rate limit + content length limit
- Daily metrics dashboard for anomaly detection

## Future
- 2FA via OTP (pyotp already in requirements) for login
- E2E encryption for messages (Signal protocol)
- Device fingerprinting for bot detection
- WAF (AWS WAF) in front of ALB

## Vulnerability Triage
- Dependency scanning via GitHub Dependabot
- `pip audit` in CI
- Sentry for exception tracking
