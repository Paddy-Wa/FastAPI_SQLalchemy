from sqlalchemy import Column, Integer, String
from database import Base

class Person(Base):
    __tablename__ = 'people'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    age = Column(Integer)
    comment = Column(String)

