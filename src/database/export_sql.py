import sqlite3
from src.config import DB_PATH, DATA_DIR


def export_sql_dumps():
    """Genera schema.sql (DDL) y seed.sql (DML) de forma independiente."""
    schema_file = DATA_DIR / "schema.sql"
    seed_file = DATA_DIR / "seed.sql"

    if not DB_PATH.exists():
        print(f"Error: No se encuentra la base de datos en {DB_PATH}.")
        return

    con = sqlite3.connect(DB_PATH)
    cursor = con.cursor()

    # 1. Extraer DDL (schema.sql): tablas e indices
    cursor.execute("SELECT sql FROM sqlite_master WHERE sql IS NOT NULL AND type IN ('table', 'index');")
    ddl_statements = [row[0] + ";" for row in cursor.fetchall()]

    with open(schema_file, "w", encoding="utf-8") as f:
        f.write("-- ========================================================\n")
        f.write("-- DDL: Definicion de Esquema y Relaciones de Base de Datos\n")
        f.write("-- ========================================================\n\n")
        f.write("\n\n".join(ddl_statements))
        f.write("\n")

    # 2. Extraer DML (seed.sql): sentencias de insercion
    with open(seed_file, "w", encoding="utf-8") as f:
        f.write("-- ========================================================\n")
        f.write("-- DML: Datos Iniciales (Seed - Contratistas y Puntos)\n")
        f.write("-- ========================================================\n\n")
        for line in con.iterdump():
            if line.startswith("INSERT INTO") and not line.startswith("INSERT INTO sqlite_"):
                f.write(f"{line}\n")

    con.close()
    print(f"Archivos exportados exitosamente:\n  - {schema_file}\n  - {seed_file}")


if __name__ == "__main__":
    export_sql_dumps()