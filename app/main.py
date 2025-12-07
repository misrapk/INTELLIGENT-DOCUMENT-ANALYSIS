from fastapi import FastAPI, HTTPException, Depends, status, UploadFile, File
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from databases import Database
from sqlalchemy import Table, Column, Integer, String, DateTime, ForeignKey, MetaData
from passlib.context import CryptContext
from jose import jwt, JWTError
from pydantic import BaseModel
from datetime import datetime, timedelta
from app.document_processor import extract_text_from_pdf
from app.ai_workflow import generate_health_scores, summarize_health_report
from app.models import documents, metadata, users, database
import os
import sqlalchemy
import requests

# Import your pdf extraction code
from app.document_processor import extract_text_from_pdf

# Constants (replace SECRET_KEY with your secure value)
DATABASE_URL = "sqlite:///./test.db"
SECRET_KEY = "your_very_secret_key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Initialize FastAPI app
app = FastAPI() 

# Initialize the database and metadata ONLY ONCE here for all tables!
database = Database(DATABASE_URL)
# metadata = MetaData()

# # Define Users table
# users = Table(
#     "users",
#     metadata,
#     Column("id", Integer, primary_key=True),
#     Column("username", String(50), unique=True, index=True),
#     Column("email", String(100), unique=True, index=True),
#     Column("hashed_password", String(255)),
# )

# # Define Documents table
# documents = Table(
#     "documents",
#     metadata,
#     Column("id", Integer, primary_key=True),
#     Column("user_id", Integer, ForeignKey("users.id")),
#     Column("filename", String(100)),
#     Column("summary", String(1000)),
#     Column("upload_time", DateTime, default=datetime.utcnow),
# )

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 scheme for Bearer token authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Pydantic models for request/response validation
class UserCreate(BaseModel):
    username: str
    email: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str
    
#summarise the pdf
def perplexity_summarize(text: str) -> str:
    api_url = "https://api.perplexity.ai/v1/answer"  # Use your endpoint if different
    api_key = "YOUR_PERPLEXITY_API_KEY"  # Set your own key here

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "pplx-7b-chat",  # Or pplx-70b-chat if you have access
        "messages": [
            {"role": "system", "content": "You are a friendly assistant that makes patient health reports easy to understand."},
            {"role": "user", "content": f"Summarize this health report for a patient in simple, clear language:\n{text}"}
        ],
        "max_tokens": 300,
        "temperature": 0.7
    }
    try:
        response = requests.post(api_url, headers=headers, json=data)
        response.raise_for_status()
        summary = response.json()["choices"][0]["message"]["content"]
        return summary
    except Exception as e:
        return "(Perplexity summary unavailable.)"


# Hash password before saving
def hash_password(password: str) -> str:
    return pwd_context.hash(password)

# Verify password on login
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

# Create JWT access token
def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt
   

# Dependency to get current logged-in user by decoding JWT token
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

# Create tables and connect to DB on startup
@app.on_event("startup")
async def startup():
    await database.connect()
    engine = sqlalchemy.create_engine(DATABASE_URL)
    print("🔧 Creating tables...")  # Add this
    metadata.create_all(engine)  # This creates all tables defined in metadata
    print("🔧 CREATED tables...")  # Add this
    

# Disconnect DB on shutdown
@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()

# Signup endpoint allows users to register
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

# Login endpoint generates JWT token after verifying credentials
@app.post("/token", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    query = users.select().where(users.c.username == form_data.username)
    user = await database.fetch_one(query)
    if not user or not verify_password(form_data.password, user["hashed_password"]):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password")
    access_token = create_access_token(data={"sub": user["username"]})
    return {"access_token": access_token, "token_type": "bearer"}

# An example protected route returning user info
@app.get("/me")
async def read_users_me(current_user: dict = Depends(get_current_user)):
    return {"username": current_user["username"], "email": current_user["email"]}

# Endpoint to get documents owned by current logged-in user
@app.get("/my-documents")
async def get_my_documents(current_user: dict = Depends(get_current_user)):
    query = documents.select().where(documents.c.user_id == current_user["id"])
    docs = await database.fetch_all(query)
    return [
        {
            "filename": doc["filename"],
            "summary": doc["summary"],
            "upload_time": doc["upload_time"].isoformat() if doc["upload_time"] else "",
        }
        for doc in docs
    ]

# Endpoint to upload PDF and extract text (as example)
@app.post("/extract-text")
async def extract_text_from_file(file: UploadFile = File(...), current_user: dict = Depends(get_current_user)):
    contents = await file.read()
    temp_dir = "temp_files"
    os.makedirs(temp_dir, exist_ok=True)
    temp_path = os.path.join(temp_dir, file.filename)
    with open(temp_path, "wb") as f:
        f.write(contents)
    extracted_text = extract_text_from_pdf(temp_path)
    os.remove(temp_path)  # cleanup temporary file
    
    #ai summary
    ai_summary = summarize_health_report(extracted_text)
    
    #generate health Score
    health_scores = generate_health_scores(extracted_text)
    # Save file info and summary to documents table
    query = documents.insert().values(
        user_id=current_user["id"],
        filename=file.filename,
        summary=ai_summary,        # or a processed summary
        overall_health_score=health_scores["overall_health_score"],
        physical_health_score=health_scores["physical_health_score"],
        mental_health_score=health_scores["mental_health_score"],
        internal_health_score=health_scores["internal_health_score"],
        upload_time=datetime.utcnow()  # optional, default may already be set
    )
    await database.execute(query)
    
    return {"filename": file.filename, "extracted_text": ai_summary, "health_scores":health_scores}


@app.get("/health-dashboard")
async def get_health_dashboard(current_user: dict = Depends(get_current_user)):
    query= documents.select().where(documents.c.user_id == current_user["id"])
    docs = await database.fetch_all(query)
    
    if not docs:
        # No documents uploaded yet
        return {
            "has_documents": False,
            "overall_health_score": 0,
            "physical_health_score": 0,
            "mental_health_score": 0,
            "internal_health_score": 0,
            "message": "No health reports uploaded yet. Upload your first report to get health scores.",
        }
    # Calculate averages from all documents
    overall_avg = sum(doc["overall_health_score"] for doc in docs) / len(docs)
    physical_avg = sum(doc["physical_health_score"] for doc in docs) / len(docs)
    mental_avg = sum(doc["mental_health_score"] for doc in docs) / len(docs)
    internal_avg = sum(doc["internal_health_score"] for doc in docs) / len(docs)

    return {
        "has_documents": True,
        "overall_health_score": round(overall_avg, 1),
        "physical_health_score": round(physical_avg, 1),
        "mental_health_score": round(mental_avg, 1),
        "internal_health_score": round(internal_avg, 1),
        "document_count":len(docs)
    }