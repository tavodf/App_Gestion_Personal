import math
from datetime import datetime
from typing import List, Dict, Any
from sqlalchemy.orm import Session

from src.database.connection import SessionLocal
from src.database.models import Contratista, PuntoOperacion, Asignacion, EstadoContratista, NivelCriticidad


class AllocationEngine:
    def __init__(self, db: Session):
        self.db = db

    def generar_plan_diario(
        self,
        fecha_inicio: datetime,
        fecha_fin: datetime,
        ratio_buffer: float = 0.12
    ) -> Dict[str, Any]:
        """
        Ejecuta la asignacion determinista para una ventana de operacion.
        Garantiza reserva de buffer movil y cobertura por criticidad.
        """
        # 1. Obtener contratistas disponibles
        contratistas = (
            self.db.query(Contratista)
            .filter(Contratista.estado == EstadoContratista.DISPONIBLE)
            .all()
        )
        total_disponibles = len(contratistas)
        if total_disponibles == 0:
            raise ValueError("No hay contratistas disponibles para programar.")

        # 2. Separar buffer movil (reemplazos inmediatos)
        tamano_buffer = max(1, math.floor(total_disponibles * ratio_buffer))
        equipo_buffer = contratistas[:tamano_buffer]
        pool_terreno = contratistas[tamano_buffer:]

        # 3. Obtener puntos ordenados por criticidad
        orden_criticidad = {
            NivelCriticidad.ALTA: 1,
            NivelCriticidad.MEDIA: 2,
            NivelCriticidad.BAJA: 3,
        }
        puntos = self.db.query(PuntoOperacion).all()
        puntos_ordenados = sorted(puntos, key=lambda p: orden_criticidad.get(p.criticidad, 99))

        asignaciones: List[Asignacion] = []

        # 4. Registrar asignaciones del buffer movil
        for c in equipo_buffer:
            asignaciones.append(
                Asignacion(
                    contratista_id=c.id,
                    punto_id=None,
                    inicio=fecha_inicio,
                    fin=fecha_fin,
                    es_buffer_movil=True,
                    activa=True,
                )
            )

        # 5. Cobertura de dotacion minima en terreno
        idx_contratista = 0
        total_terreno = len(pool_terreno)

        for punto in puntos_ordenados:
            requeridos = punto.requerimiento_minimo
            for _ in range(requeridos):
                if idx_contratista < total_terreno:
                    c = pool_terreno[idx_contratista]
                    asignaciones.append(
                        Asignacion(
                            contratista_id=c.id,
                            punto_id=punto.id,
                            inicio=fecha_inicio,
                            fin=fecha_fin,
                            es_buffer_movil=False,
                            activa=True,
                        )
                    )
                    idx_contratista += 1

        # 6. Repartir excedente en puntos de criticidad ALTA
        puntos_alta = [p for p in puntos_ordenados if p.criticidad == NivelCriticidad.ALTA]
        while idx_contratista < total_terreno:
            for punto in puntos_alta:
                if idx_contratista < total_terreno:
                    c = pool_terreno[idx_contratista]
                    asignaciones.append(
                        Asignacion(
                            contratista_id=c.id,
                            punto_id=punto.id,
                            inicio=fecha_inicio,
                            fin=fecha_fin,
                            es_buffer_movil=False,
                            activa=True,
                        )
                    )
                    idx_contratista += 1
                else:
                    break

        # 7. Persistir asignaciones en bloque
        self.db.add_all(asignaciones)
        self.db.commit()

        return {
            "total_programados": len(asignaciones),
            "buffer_movil": len(equipo_buffer),
            "asignados_terreno": len(asignaciones) - len(equipo_buffer),
        }


def test_run():
    db = SessionLocal()
    try:
        engine = AllocationEngine(db)
        inicio = datetime(2026, 9, 20, 7, 0)
        fin = datetime(2026, 9, 20, 15, 0)
        resumen = engine.generar_plan_diario(inicio, fin)
        print("Resultado de la asignacion:")
        for k, v in resumen.items():
            print(f"  - {k}: {v}")
    finally:
        db.close()


if __name__ == "__main__":
    test_run()