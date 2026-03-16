from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, Float
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    profile_url = Column(String, unique=True)
    username = Column(String)
    full_name = Column(String)
    headline = Column(String)
    profile_image = Column(String)
    last_scraped = Column(DateTime)

class Post(Base):
    __tablename__ = "posts"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    post_id = Column(String)
    post_text = Column(Text)
    post_date = Column(DateTime)
    likes = Column(Integer)
    comments = Column(Integer)
    reposts = Column(Integer)
    impressions = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)

class Reaction(Base):
    __tablename__ = "reactions"
    id = Column(Integer, primary_key=True)
    post_id = Column(Integer, ForeignKey("posts.id"))
    reactor_name = Column(String)
    reaction_type = Column(String)
    reacted_at = Column(DateTime, default=datetime.utcnow)

class Comment(Base):
    __tablename__ = "comments"
    id = Column(Integer, primary_key=True)
    post_id = Column(Integer, ForeignKey("posts.id"))
    commenter_name = Column(String)
    comment_text = Column(Text)
    comment_date = Column(DateTime)

class ProfileUpdate(Base):
    __tablename__ = "profile_updates"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    update_type = Column(String)
    update_text = Column(Text)
    update_date = Column(DateTime, default=datetime.utcnow)

class EngagementMetric(Base):
    __tablename__ = "engagement_metrics"
    id = Column(Integer, primary_key=True)
    post_id = Column(Integer, ForeignKey("posts.id"))
    likes = Column(Integer)
    comments = Column(Integer)
    reposts = Column(Integer)
    engagement_rate = Column(Float)
    recorded_at = Column(DateTime, default=datetime.utcnow)