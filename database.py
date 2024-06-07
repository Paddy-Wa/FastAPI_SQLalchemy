from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from os import getcwd

app_path = getcwd()

SQLALCHEMY_DATABASE_URL = (f'sqlite:///{app_path}/local.db')

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread":False}
)

Sessionlocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
