from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import declarative_base

databases = 'sqlite:///user.sqlite'
engine = create_engine(databases, connect_args={"check_same_thread": False})
begin = sessionmaker(bind=engine, autocommit = False, autoflush=False)
data = declarative_base()