from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from models import Base, User, Bookmark
from auth import hash_password, verify_password, create_access_token
from utils import fetch_metadata, fetch_summary
from pydantic import BaseModel
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
app=FastAPI()


SECRET_KEY = "supersecret"
ALGORITHM = "HS256"
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],  
    allow_headers=["*"],
)
engine = create_engine("sqlite:///db.sqlite3", connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine)
Base.metadata.create_all(bind=engine)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

class UserCreate(BaseModel):
    email: str
    password: str

class BookmarkCreate(BaseModel):
    url: str
    tag: str = "general"  
    position: int = 0
@app.post("/dev-get-token")
def dev_get_token(email: str, password: str):
    db = SessionLocal()
    user = db.query(User).filter(User.email == email).first()
    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Invalid login")
    token = create_access_token({"sub": email})
    return {"token": token}

@app.post("/register")
def register(user: UserCreate):
    db = SessionLocal()
    if db.query(User).filter(User.email == user.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    hashed_password = hash_password(user.password)
    db_user = User(email=user.email, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return {"email": db_user.email}

@app.post("/login")
def login(from_data: OAuth2PasswordRequestForm = Depends()):
    db = SessionLocal()
    user = db.query(User).filter(User.email == from_data.username).first()
    if not user or not verify_password(from_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}

def get_current_user(token: str = Depends(oauth2_scheme)):
    from jose import JWTError, jwt
    try:
        payload =jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        user_id: str = payload.get("sub")
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=401, detail="Invalid authentication credentials")
        db = SessionLocal()
        user = db.query(User).filter(User.email == email).first()
        if user is None:
            raise HTTPException(status_code=401, detail="Invalid authentication credentials")   
        return user
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")
    

@app.post("/bookmarks", response_model=BookmarkCreate)
def create_bookmark(bookmark: BookmarkCreate, current_user: User = Depends(get_current_user)):
    db = SessionLocal()
    title, favicon = fetch_metadata(bookmark.url)
    summary = fetch_summary(bookmark.url)

    db_bookmark = Bookmark(
        url=bookmark.url,
        title=title,
        favicon=favicon,
        summary=summary,
        tag=bookmark.tag,
        position=bookmark.position,
        user_id=current_user.id
    )
    db.add(db_bookmark)
    db.commit()
    db.refresh(db_bookmark)
    return db_bookmark


@app.get("/bookmarks")
def get_bookmarks(current_user: User = Depends(get_current_user)):
    db = SessionLocal()
    bookmarks = (
        db.query(Bookmark)
        .filter(Bookmark.user_id == current_user.id)
        .order_by(Bookmark.position)
        .all()
    )
    return bookmarks

@app.delete("/bookmarks/{bookmark_id}")
def delete_bookmark(bookmark_id: int, current_user: User = Depends(get_current_user)):
    db = SessionLocal()
    bookmark = db.query(Bookmark).filter(Bookmark.id == bookmark_id, Bookmark.user_id == current_user.id).first()
    if not bookmark:
        raise HTTPException(status_code=404, detail="Bookmark not found")
    db.delete(bookmark)
    db.commit()
    return {"detail": "Bookmark deleted successfully"}
from typing import List

class ReorderItem(BaseModel):
    id: int
    position: int

@app.post("/bookmarks/reorder")
def reorder_bookmarks(order: List[ReorderItem], current_user: User = Depends(get_current_user)):
    db = SessionLocal()
    for item in order:
        bookmark = db.query(Bookmark).filter(Bookmark.id == item.id, Bookmark.user_id == current_user.id).first()
        if bookmark:
            bookmark.position = item.position
    db.commit()
    return {"detail": "Reorder successful"}


import uvicorn
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
