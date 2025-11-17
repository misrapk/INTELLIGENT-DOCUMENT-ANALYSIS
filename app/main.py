from fastapi import FastAPI, HTTPException, Depends, status, UploadFile, File
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from databases import Database
from sqlalchemy import Table, Column, Integer, String, MetaData
from passlib.context import CryptContext
from jose import jwt, JWTError
from pydantic import BaseModel
from datetime import datetime, timedelta
from app.models import database, documents  
import os

# Constants (replace SECRET_KEY with your secure value)
DATABASE_URL = "sqlite:///./test.db"
SECRET_KEY = "your_very_secret_key"  
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Initialize FastAPI and database
app = FastAPI()
database = Database(DATABASE_URL)
metadata = MetaData()


#TODO: User Account
# Users table definition
users = Table(
    "users",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("username", String(50), unique=True, index=True),
    Column("email", String(100), unique=True, index=True),
    Column("hashed_password", String(255)),
)

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 scheme for Bearer tokens
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Pydantic models for user creation and token response
class UserCreate(BaseModel):
    username: str
    email: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

# Utility functions
def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    query = users.select().where(users.c.username == username)
    user = await database.fetch_one(query)
    if user is None:
        raise credentials_exception
    return user

# Events to connect/disconnect database
@app.on_event("startup")
async def startup():
    await database.connect()
    # Create tables if not exist
    query = """CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                username TEXT UNIQUE,
                email TEXT UNIQUE,
                hashed_password TEXT
                )"""
    await database.execute(query=query)

@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()

# Signup endpoint
@app.post("/signup", status_code=201)
async def signup(user: UserCreate):
    query = users.select().where(users.c.username == user.username)
    existing_user = await database.fetch_one(query)
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    hashed_pw = hash_password(user.password)
    query = users.insert().values(username=user.username, email=user.email, hashed_password=hashed_pw)
    await database.execute(query)
    return {"message": "User created successfully"}

# Token (login) endpoint
@app.post("/token", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    query = users.select().where(users.c.username == form_data.username)
    user = await database.fetch_one(query)
    if not user or not verify_password(form_data.password, user["hashed_password"]):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password")
    access_token = create_access_token(data={"sub": user["username"]})
    return {"access_token": access_token, "token_type": "bearer"}

# Protected user info endpoint
@app.get("/me")
async def read_users_me(current_user: dict = Depends(get_current_user)):
    return {"username": current_user["username"], "email": current_user["email"]}

# TODO: Endpoint to get logged-in user's documents
@app.get("/my-documents")
async def get_my_documents(current_user: dict = Depends(get_current_user)):
    """
    Returns a list of documents (filename, summary, upload time)
    owned by the current authenticated user.
    """
    query = documents.select().where(documents.c.user_id == current_user["id"])
    docs = await database.fetch_all(query)
    
    #format for frontend
    return [
        {
            "filename" : doc["filename"],
            "summary": doc["summary"],
            "upload_time": doc["upload_time"].isoformat() if doc["upload_time"] else "",
        }
        for doc in docs
    ]

# PDF Extraction utility (example)
from app.document_processor import extract_text_from_pdf  # import your extraction code here

# Protected PDF extract endpoint
@app.post("/extract-text")
async def extract_text_from_file(file: UploadFile = File(...), current_user: dict = Depends(get_current_user)):
    contents = await file.read()
    temp_dir = "temp_files"
    os.makedirs(temp_dir, exist_ok=True)
    temp_path = os.path.join(temp_dir, file.filename)
    with open(temp_path, "wb") as f:
        f.write(contents)
    extracted_text = extract_text_from_pdf(temp_path)
    os.remove(temp_path)  # cleanup temp file
    return {"filename": file.filename, "extracted_text": extracted_text}
