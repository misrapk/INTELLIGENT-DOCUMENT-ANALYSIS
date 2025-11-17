from sqlalchemy import ForeignKey, Table, Column, Integer, String, MetaData, DateTime
from databases import Database
import datetime

DB_URL = "sqlite:///./test.db"

database = Database(DB_URL)
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
    Column("upload_time", DateTime, default=datetime.datetime.utcnow)

)