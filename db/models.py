# db/models.py
from sqlalchemy import Column, BigInteger, Text, TIMESTAMP, text
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class UserVideo(Base):
    __tablename__ = "user_videos"

    user_id = Column(BigInteger, primary_key=True)
    url = Column(Text, primary_key=True)
    added_at = Column(TIMESTAMP, server_default=text("now()"))
    region = Column(Text, nullable=True)
    suffix = Column(Text, nullable=True)