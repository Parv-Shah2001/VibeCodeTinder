"""
Seed script for VibeCodeTinder
Creates 100 demo users with profiles, photos, and some swipes/matches/messages
Designed to showcase scalability patterns.
"""
import os
import sys
import random
from datetime import datetime, timedelta

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import SessionLocal, init_db
from app.modules.auth.models import User
from app.modules.users.models import Profile, UserPreference
from app.modules.media.models import MediaAsset
from app.core.security import hash_password
from faker import Faker

# Try to import faker, fallback to simple generation if not available
try:
    from faker import Faker
    fake = Faker()
    HAS_FAKER = True
except ImportError:
    HAS_FAKER = False
    print("faker not installed, using simple random data. pip install faker for richer seed.")

init_db()
db = SessionLocal()

FIRST_NAMES = ["Alex", "Jordan", "Taylor", "Morgan", "Casey", "Riley", "Avery", "Emma", "Olivia", "Noah", "Liam", "Ava", "Sophia", "Mia", "Ethan", "Lucas", "Amelia", "Harper", "Evelyn", "Abigail"]
LAST_NAMES = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez", "Martinez"]
CITIES = [
    ("New York", 40.7128, -74.0060),
    ("Los Angeles", 34.0522, -118.2437),
    ("Chicago", 41.8781, -87.6298),
    ("Houston", 29.7604, -95.3698),
    ("Miami", 25.7617, -80.1918),
    ("San Francisco", 37.7749, -122.4194),
    ("Seattle", 47.6062, -122.3321),
    ("Austin", 30.2672, -97.7431),
    ("Boston", 42.3601, -71.0589),
    ("Phoenix", 33.4484, -112.0740),
]
BIOS = [
    "Adventurous soul 🌍 | Coffee enthusiast ☕ | Dog mom 🐶",
    "Software engineer by day, DJ by night 🎧",
    "Gym rat 💪 | Travel junkie ✈️ | Let's explore the world together",
    "Book lover 📚 | Hiking addict 🥾 | Looking for genuine connection",
    "Entrepreneur | Fitness freak | Foodie 🍜 | Let's grab brunch?",
    "Yoga instructor 🧘‍♀️ | Plant parent 🌱 | Positivity only",
    "No bio, just vibes ✨",
    "Engineer, climber, chef in training 👨‍🍳",
    "Former athlete 🏀 now into startups and good conversations",
    "Artist 🎨 | Dreamer | Make me laugh and you're halfway there",
]
JOBS = ["Software Engineer", "Product Manager", "Designer", "Marketing Manager", "Doctor", "Teacher", "Entrepreneur", "Photographer", "Chef", "Writer", None]
SCHOOLS = ["Stanford", "MIT", "Harvard", "NYU", "UCLA", "University of Texas", "Columbia", None]

def random_user(i):
    email = f"user{i}@vibe.test"
    existing = db.query(User).filter(User.email == email).first()
    if existing:
        return existing
    user = User(email=email, hashed_password=hash_password("password123"), is_verified=random.random() > 0.3)
    db.add(user)
    db.flush()
    # Profile
    first = random.choice(FIRST_NAMES)
    last = random.choice(LAST_NAMES)
    city, lat, lon = random.choice(CITIES)
    # jitter lat lon
    lat += random.uniform(-0.3, 0.3)
    lon += random.uniform(-0.3, 0.3)
    birth = datetime.now() - timedelta(days=random.randint(18*365, 35*365))
    profile = Profile(
        user_id=user.id,
        display_name=f"{first} {last[0]}.",
        bio=random.choice(BIOS),
        birthdate=birth,
        gender=random.choice(["male", "female", "nonbinary"]),
        interested_in=random.choice(["male", "female", "everyone"]),
        latitude=lat,
        longitude=lon,
        city=city,
        job_title=random.choice(JOBS),
        school=random.choice(SCHOOLS),
        elo_score=random.uniform(800, 1200),
        is_boosted=random.random() > 0.85,
        is_verified=user.is_verified,
        show_me=True,
    )
    db.add(profile)
    db.flush()
    pref = UserPreference(
        profile_id=profile.id,
        min_age=random.randint(18, 25),
        max_age=random.randint(26, 40),
        max_distance_km=random.choice([10, 20, 50, 100]),
        show_me=random.choice(["male", "female", "everyone"]),
        global_mode=False,
    )
    db.add(pref)
    # Media - use pravatar / picsum
    num_photos = random.randint(1, 5)
    for j in range(num_photos):
        asset = MediaAsset(
            user_id=user.id,
            storage_key=f"profile/seed_{user.id}_{j}.jpg",
            public_url=f"https://i.pravatar.cc/400?img={random.randint(1,70)}",
            thumbnail_url=f"https://i.pravatar.cc/150?img={random.randint(1,70)}",
            media_type="image",
            status="ready",
            is_primary=(j==0),
            display_order=j,
            width=400,
            height=600,
        )
        db.add(asset)
    return user

def main(n=100):
    print(f"Seeding {n} demo users...")
    users = []
    for i in range(1, n+1):
        u = random_user(i)
        users.append(u)
        if i % 20 == 0:
            db.commit()
            print(f"  {i}/{n} users created")
    db.commit()
    print(f"Created {len(users)} users")

    # Create some swipes & matches for user1
    from app.modules.swipes.models import Swipe
    from app.modules.matches.models import Match
    from app.modules.messaging.models import Conversation, Message

    user1 = users[0]
    print(f"Creating swipes for {user1.email}...")
    for target in users[1:30]:
        if random.random() > 0.5:
            s_type = random.choice(["like", "like", "like", "dislike", "superlike"])
            # avoid dup
            if not db.query(Swipe).filter(Swipe.swiper_id==user1.id, Swipe.swiped_id==target.id).first():
                swipe = Swipe(swiper_id=user1.id, swiped_id=target.id, swipe_type=s_type)
                db.add(swipe)
                # 30% mutual like chance
                if s_type in ("like","superlike") and random.random() > 0.6:
                    if not db.query(Swipe).filter(Swipe.swiper_id==target.id, Swipe.swiped_id==user1.id).first():
                        db.add(Swipe(swiper_id=target.id, swiped_id=user1.id, swipe_type="like"))
                        u1,u2 = sorted([user1.id, target.id])
                        if not db.query(Match).filter(Match.user1_id==u1, Match.user2_id==u2).first():
                            m = Match(user1_id=u1, user2_id=u2)
                            db.add(m)
                            db.flush()
                            conv = Conversation(user1_id=u1, user2_id=u2, last_message_text="Hey 👋", last_message_at=datetime.utcnow())
                            db.add(conv)
                            db.flush()
                            msg = Message(conversation_id=conv.id, sender_id=target.id, content="Hey! It's a match 🎉", message_type="text")
                            db.add(msg)
    db.commit()
    print("Seed complete! Login with user1@vibe.test / password123")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--count", type=int, default=100)
    args = parser.parse_args()
    main(args.count)
