from sqlalchemy import ForeignKey, Table, Column, Integer, String, MetaData, DateTime, Float
from databases import Database
import datetime

DATABASE_URL = "sqlite:///./test.db"

database = Database(DATABASE_URL)
metadata = MetaData()


users = Table(
    "users", 
    metadata,
    Column("id", Integer, primary_key = True),
    Column("username", String(50), unique=True, index = True),
    Column("email", String(100), unique=True, index = True),
    Column("hashed_password", String(255)),
)

documents = Table(
    "documents", 
    metadata,
    Column("id", Integer, primary_key = True),
    Column("user_id", Integer,ForeignKey("users.id")),
    Column("filename", String(100)),
    Column("summary", String(1000)),
    Column("upload_time", DateTime, default=datetime.datetime.utcnow),
    
    #for health score
    Column("overall_health_score", Float, default=0.0), 
    Column("physical_health_score", Float, default=0.0), 
    Column("mental_health_score", Float, default=0.0), 
    Column("internal_health_score", Float, default=0.0)
    

)