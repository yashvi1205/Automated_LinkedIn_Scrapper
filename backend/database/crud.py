from .db import SessionLocal
from .models import User

def save_user(profile_url):

    db = SessionLocal()

    existing = db.query(User).filter(User.profile_url == profile_url).first()

    if existing:
        print("User already exists:", profile_url)
        db.close()
        return

    new_user = User(profile_url=profile_url)

    db.add(new_user)
    db.commit()

    print("User saved:", profile_url)

    db.close()