from typing import cast
from sqlalchemy import create_engine, engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from decouple import config

SQLALCHEMY_DATABASE_URL = config('SQLALCHEMY_DATABASE_URL', cast=str)

engine= create_engine(SQLALCHEMY_DATABASE_URL, connect_args={'check_same_thread': False})

# Local session for thread safety (handled by sqlalchemy)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Metadata object where newly defined tables are collected
Base = declarative_base()