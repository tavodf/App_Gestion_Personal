import random
from sqlalchemy.orm import Session
from src.database.connection import SessionLocal
from src.database.models import (
    Contratista,
    PuntoOperacion,
    EstadoContratista,
    NivelCriticidad,
)

NOMBRES = [
    "Carlos", "Andres", "Luisa", "Camila", "Jorge", "Diana", "Felipe", "Paola",
    "Hernan", "Natalia", "Mauricio", "Andrea", "David", "Sandra", "Alejandro",
    "Patricia", "Daniel", "Claudia", "Julian", "Monica", "Sebastian", "Maria"
]
APELLIDOS = [
    "Rodriguez", "Gomez", "Lopez", "Martinez", "Perez", "Garcia", "Sanchez",
    "Torres", "Ramirez", "Flores", "Vargas", "Castro", "Morales", "Suarez"
]

ROLES = [
    ("Gestor Territorial", 45),
    ("Lider de Operacion", 10),
    ("Enlace Institucional", 5)
]

PUNTOS_TERRENO = [
    {"nombre": "Poligono Centro - Eje Ambiental", "sector": "UPZ Central", "criticidad": NivelCriticidad.ALTA, "min": 6},
    {"nombre": "Estacion de Transferencia TransMilenio", "sector": "UPZ Oriental", "criticidad": NivelCriticidad.ALTA, "min": 5},
    {"nombre": "Plaza de Mercado Central", "sector": "UPZ Comercial", "criticidad": NivelCriticidad.MEDIA, "min": 4},
    {"nombre": "Corredor Comercial Peatonal", "sector": "UPZ Central", "criticidad": NivelCriticidad.MEDIA, "min": 4},
    {"nombre": "Parque Metropolitano Sector A", "sector": "UPZ Recreativa", "criticidad": NivelCriticidad.BAJA, "min": 2},
    {"nombre": "Parque Metropolitano Sector B", "sector": "UPZ Recreativa", "criticidad": NivelCriticidad.BAJA, "min": 2},
    {"nombre": "Punto de Control Interinstitucional", "sector": "UPZ Norte", "criticidad": NivelCriticidad.ALTA, "min": 4},
    {"nombre": "Corredor Gastronomico y Cultural", "sector": "UPZ Historica", "criticidad": NivelCriticidad.MEDIA, "min": 3},
]


def poblar_contratistas(db: Session, total: int = 60):
    existentes = db.query(Contratista).count()
    if existentes >= total:
        print(f"La tabla contratistas ya cuenta con {existentes} registros. Omitiendo seed.")
        return

    contratistas = []
    doc_base = 1010203001
    
    roles_expandidos = []
    for rol, cantidad in ROLES:
        roles_expandidos.extend([rol] * cantidad)

    for i in range(total):
        nombre = f"{random.choice(NOMBRES)} {random.choice(APELLIDOS)}"
        contratista = Contratista(
            documento=str(doc_base + i),
            nombre=nombre,
            rol=roles_expandidos[i],
            estado=EstadoContratista.DISPONIBLE,
        )
        contratistas.append(contratista)

    db.add_all(contratistas)
    db.commit()
    print(f"Se registraron exitosamente {total} contratistas.")


def poblar_puntos(db: Session):
    if db.query(PuntoOperacion).count() > 0:
        print("Puntos de operacion ya inicializados. Omitiendo seed.")
        return

    puntos = [
        PuntoOperacion(
            nombre=p["nombre"],
            sector=p["sector"],
            criticidad=p["criticidad"],
            requerimiento_minimo=p["min"],
        )
        for p in PUNTOS_TERRENO
    ]
    db.add_all(puntos)
    db.commit()
    print(f"Se registraron exitosamente {len(puntos)} puntos territoriales.")


def run_seed():
    db: Session = SessionLocal()
    try:
        poblar_contratistas(db, total=60)
        poblar_puntos(db)
    finally:
        db.close()


if __name__ == "__main__":
    run_seed()