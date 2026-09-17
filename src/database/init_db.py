from src.database.connection import engine, Base
from src.database.models import Contratista, PuntoOperacion, Asignacion, Novedad


def init_database():
    """Genera todas las tablas registradas en Base.metadata."""
    Base.metadata.create_all(bind=engine)
    print("Tablas creadas con exito en app.db:")
    for table_name in Base.metadata.tables.keys():
        print(f"  - {table_name}")


if __name__ == "__main__":
    init_database()
    