from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import declarative_base
from db.base import Base


class Users(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    password = Column(String)
    role = Column(String, default="user")

    def as_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "role": self.role
        }
    



