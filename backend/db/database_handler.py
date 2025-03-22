from db.base import Base
from logger import logger
from services.config_services import DB_URL
from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker


class DatabaseHandler:
    def __init__(self, db_url=DB_URL):
        try:
            self.engine = create_engine(db_url)
            Base.metadata.create_all(self.engine)
            self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)

        except Exception as e:
            logger.error(f"Error in DB Handler: {str(e)}")

    def get_session(self):
        """Create a new database session."""
        return self.SessionLocal()
