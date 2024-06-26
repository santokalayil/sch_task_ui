


from sqlalchemy import create_engine, Column, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

# Database connection string
DATABASE_URI = 'sqlite:///db.sqlite3'

# Define base class for SQLAlchemy models
Base = declarative_base()

# Define the 'logs' table schema
class Log(Base):
    __tablename__ = 'logs'

    datetime = Column(DateTime, primary_key=True)
    log_message = Column(String)
    level = Column(String)

    def __repr__(self):
        return f"<Log(datetime='{self.datetime}', log_message='{self.log_message}')>"

# Function to create or connect to the database and create tables if necessary
def create_database():
    engine = create_engine(DATABASE_URI)
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return SessionLocal()

# Function to store log messages in the database
def store_log(message, level="info"):
    try:
        # Create database and session if not already created
        session = create_database()

        # Create a new log entry
        new_log = Log(datetime=datetime.now(), log_message=message, level=level)
        session.add(new_log)
        session.commit()
        print(f"Log message successfully stored: {message}")
    except Exception as e:
        print(f"Error storing log message: {e}")


