import os
from sqlmodel import SQLModel, Field, create_engine, Session
from typing import Optional
import pymysql
from dotenv import load_dotenv
from sqlalchemy import LargeBinary

# Load the .env file
load_dotenv()

# Get the database URL from the .env file
DATABASE_URL = os.getenv("SQLALCHEMY_DATABASE_URL")

# Create the database engine
engine = create_engine(DATABASE_URL, echo=True)

# JobDetails table definition with LONGTEXT for large text fields
class JobDetails(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    category: str
    description: str = Field(sa_column=LargeBinary())  # Use LONGTEXT to store very large descriptions
    requirements: str = Field(sa_column=LargeBinary())  # Use LONGTEXT to store very large requirements

# Function to create the database and tables
def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

# Function to get the database session
def get_session():
    with Session(engine) as session:
        yield session

# Function to insert job details into the database
def insert_job_details(session: Session, category: str, description: str, requirements: str):
    try:
        job_details = JobDetails(category=category, description=description, requirements=requirements)
        session.add(job_details)
        session.commit()
        session.refresh(job_details)
        return job_details
    except Exception as e:
        print(f"Error inserting into database: {e}")
        session.rollback()
        raise