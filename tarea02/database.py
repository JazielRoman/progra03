# database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base  # Importa la base de tus modelos ORM

# URL de la base de datos (SQLite para desarrollo local)
DATABASE_URL = "sqlite:///./vuelos.db"

# Crear el motor de conexión
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}  # Necesario solo en SQLite
)

# Configurar la fábrica de sesiones
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    """
    Proporciona una sesión de base de datos a FastAPI mediante Depends().
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def crear_base_datos():
    """
    Crea las tablas en la base de datos según los modelos definidos.
    """
    Base.metadata.create_all(bind=engine)
