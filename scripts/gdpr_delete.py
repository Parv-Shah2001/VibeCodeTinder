"""
GDPR Delete – fully deletes user data across all tables + S3.
For 50M users need background job + audit log.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.core.database import SessionLocal
from app.modules.auth.models import User
from app.modules.users.models import Profile
from app.core.s3 import get_storage

def gdpr_delete(user_id: int):
    db = SessionLocal()
    storage = get_storage()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            print(f"User {user_id} not found")
            return
        # Delete media from S3
        from app.modules.media.models import MediaAsset
        assets = db.query(MediaAsset).filter(MediaAsset.user_id == user_id).all()
        for a in assets:
            storage.delete(a.storage_key)
        print(f"Deleted {len(assets)} media assets from storage")

        # Delete user cascades all via FK ondelete=CASCADE
        db.delete(user)
        db.commit()
        print(f"User {user_id} fully deleted per GDPR")
        # Audit log
        with open("gdpr_audit.log", "a") as f:
            f.write(f"Deleted user {user_id} at {__import__('datetime').datetime.utcnow()}\n")
    finally:
        db.close()

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("user_id", type=int)
    args = parser.parse_args()
    gdpr_delete(args.user_id)
