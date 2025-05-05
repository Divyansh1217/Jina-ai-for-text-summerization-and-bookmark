from sqlalchemy import Column, Integer, String, Text, ForeignKey, create_engine
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True)
    hashed_password = Column(String)

class Bookmark(Base):
    __tablename__ = 'bookmarks'
    id = Column(Integer, primary_key=True)
    url = Column(Text)
    title = Column(String)
    favicon = Column(String)
    summary = Column(Text)
    tag = Column(String, default="general")  # ✅ New
    position = Column(Integer, default=0) 
    user_id = Column(Integer, ForeignKey('users.id'))
