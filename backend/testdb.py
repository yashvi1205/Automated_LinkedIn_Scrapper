from database.db import SessionLocal
from database.models import User

db = SessionLocal()

users = db.query(User).all()

print("Total users:", len(users))

for u in users:
    print(u.profile_url)

db.close()