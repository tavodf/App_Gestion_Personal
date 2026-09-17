from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from src.config import DATABASE_URL

# Engine configurado para SQLite con verificación de hilos desactivada para CLI interactivo
engine = create_engine(
    DATABASE_URL,
    echo=False,  # Cambiar a True si se requiere depuración de queries crudas
    connect_args={"check_same_thread": False}
)

# Fábrica de sesiones para transacciones atómicas
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Base declarativa para los modelos ORM
Base = declarative_base()


def get_db():
    """Generador de contexto transaccional para operaciones con la base de datos."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()