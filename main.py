from fastapi import FastAPI, Query, Path, Body, Depends, HTTPException, status, Cookie, Header, BackgroundTasks
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from typing import Annotated
from pydantic import BaseModel, Field
from jose import jwt, JWTError
from datetime import datetime, timedelta

# -------------------
# App Config & Metadata
# -------------------
app = FastAPI(
    title="Library API",
    description="A mini library API demonstrating FastAPI features from the user guide.",
    version="1.0.0",
    contact={"name": "Admin", "email": "admin@library.com"},
    license_info={"name": "MIT"},
)

# Serve static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# -------------------
# Models
# -------------------
class Book(BaseModel):
    title: Annotated[str, Field(min_length=3, max_length=100)]
    author: Annotated[str, Field(min_length=3, max_length=50)]
    year: Annotated[int, Field(gt=0, lt=2100)]
    description: Annotated[str | None, Field(max_length=200)] = None

class User(BaseModel):
    username: str
    disabled: bool | None = False

class Token(BaseModel):
    access_token: str
    token_type: str

# -------------------
# Fake DB
# -------------------
books_db = [
    {"title": "The Hobbit", "author": "Tolkien", "year": 1937},
    {"title": "1984", "author": "Orwell", "year": 1949},
]

users_db = {
    "alice": {"username": "alice", "password": "wonderland", "disabled": False},
    "bujjy23": {"username": "bujjy23", "password": "bujjy2003", "disabled": False},
}

# -------------------
# Security: OAuth2 + JWT
# -------------------
SECRET_KEY = "supersecretkey"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def authenticate_user(username: str, password: str):
    user = users_db.get(username)
    if not user or user["password"] != password:
        return False
    return User(username=username, disabled=user["disabled"])

def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username not in users_db:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
        return User(username=username)
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

@app.post("/token", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    token = create_access_token({"sub": user.username})
    return {"access_token": token, "token_type": "bearer"}

# -------------------
# API Endpoints
# -------------------

# Query, Path, Cookie, Header
@app.get("/books/")
def list_books(
    q: Annotated[str | None, Query(example="tolkien")] = None,
    limit: Annotated[int, Query(le=10)] = 5,
    ads_id: Annotated[str | None, Cookie()] = None,
    user_agent: Annotated[str | None, Header()] = None
):
    result = books_db
    if q:
        result = [b for b in result if q.lower() in b["title"].lower() or q.lower() in b["author"].lower()]
    return {"books": result[:limit], "ads_id": ads_id, "user_agent": user_agent}

# Path param with validation
@app.get("/books/{book_id}")
def get_book(book_id: Annotated[int, Path(gt=0)]):
    if book_id > len(books_db):
        raise HTTPException(status_code=404, detail="Book not found")
    return books_db[book_id - 1]

# Body params
@app.post("/books/")
def create_book(book: Book, background_tasks: BackgroundTasks):
    books_db.append(book.dict())
    # background task (e.g., log entry)
    background_tasks.add_task(print, f"New book added: {book.title}")
    return {"message": "Book added", "book": book}

# Protected endpoint
@app.get("/users/me")
def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user

# File response
@app.get("/download/sample")
def download_sample():
    return FileResponse("static/sample.txt", filename="sample.txt")

# Custom response
@app.get("/custom-response/")
def custom_response():
    return JSONResponse(content={"status": "ok", "time": str(datetime.utcnow())})
