# database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Puedes usar SQLite para pruebas locales, pero puedes cambiar la URL para PostgreSQL, MySQL, etc.
DATABASE_URL = "sqlite:///./vuelos.db"

# Crear el motor de conexión
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}  # Solo necesario para SQLite
)

# Crear una sesión de base de datos
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)