from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy_utils import UUIDType
import uuid

from database import Base


class Sleep(Base):
    __tablename__ = "sleeps"

    id = Column(
        UUIDType(binary=False), primary_key=True, index=True, default=uuid.uuid4
    )
    things = relationship("Thing", back_populates="owner")


class Thing(Base):
    __tablename__ = "things"

    id = Column(Integer, primary_key=True, index=True)
    number = Column(Integer)
    name = Column(String)
    owner_id = Column(UUIDType(binary=False), ForeignKey("sleeps.id"))

    owner = relationship("Sleep", back_populates="things")
