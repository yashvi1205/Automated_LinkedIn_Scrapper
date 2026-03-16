from .db import SessionLocal
from .models import User, Post, Reaction, Comment, ProfileUpdate, EngagementMetric
from datetime import datetime

def save_user(profile_url, username=None, full_name=None, headline=None, profile_image=None):
    db = SessionLocal()
    user = db.query(User).filter(User.profile_url==profile_url).first()
    if not user:
        user = User(
            profile_url=profile_url,
            username=username,
            full_name=full_name,
            headline=headline,
            profile_image=profile_image,
            last_scraped=datetime.utcnow()
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    else:
        user.last_scraped = datetime.utcnow()
        db.commit()
    db.close()
    return user.id

def save_post(user_id, post_id, post_text, post_date, likes, comments_count, reposts, impressions):
    db = SessionLocal()
    post = Post(
        user_id=user_id,
        post_id=post_id,
        post_text=post_text,
        post_date=post_date,
        likes=likes,
        comments=comments_count,
        reposts=reposts,
        impressions=impressions
    )
    db.add(post)
    db.commit()
    db.refresh(post)
    db.close()
    return post.id

def save_reaction(post_id, reactor_name, reaction_type):
    db = SessionLocal()
    reaction = Reaction(
        post_id=post_id,
        reactor_name=reactor_name,
        reaction_type=reaction_type
    )
    db.add(reaction)
    db.commit()
    db.close()

def save_comment(post_id, commenter_name, comment_text, comment_date):
    db = SessionLocal()
    comment = Comment(
        post_id=post_id,
        commenter_name=commenter_name,
        comment_text=comment_text,
        comment_date=comment_date
    )
    db.add(comment)
    db.commit()
    db.close()

def save_profile_update(user_id, update_type, update_text):
    db = SessionLocal()
    update = ProfileUpdate(
        user_id=user_id,
        update_type=update_type,
        update_text=update_text
    )
    db.add(update)
    db.commit()
    db.close()

def save_engagement(post_id, likes, comments, reposts, engagement_rate):
    db = SessionLocal()
    metric = EngagementMetric(
        post_id=post_id,
        likes=likes,
        comments=comments,
        reposts=reposts,
        engagement_rate=engagement_rate
    )
    db.add(metric)
    db.commit()
    db.close()