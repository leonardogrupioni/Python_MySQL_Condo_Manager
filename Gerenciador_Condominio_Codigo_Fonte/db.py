from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Altere as credenciais 
DB_URL = "mysql+mysqlconnector://root:leo2003@localhost/condominio"

engine = create_engine(DB_URL, echo=False, pool_pre_ping=True, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()
