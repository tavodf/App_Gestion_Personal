from datetime import datetime
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session

from src.database.connection import SessionLocal
from src.database.models import (
    Contratista,
    Asignacion,
    Novedad,
    EstadoContratista,
    TipoNovedad,
)


class ContingencyService:
    def __init__(self, db: Session):
        self.db = db

    def registrar_baja_y_reemplazar(
        self,
        contratista_id: int,
        tipo_novedad: TipoNovedad,
        detalle: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Registra una contingencia operativa, extrae un elemento del buffer movil
        y ejecuta la sustitucion inmediata en el punto asignado.
        """
        # 1. Validar que el contratista exista y este en terreno
        contratista_baja = self.db.query(Contratista).filter(Contratista.id == contratista_id).first()
        if not contratista_baja:
            raise ValueError(f"Contratista ID {contratista_id} no encontrado.")

        # Buscar asignacion activa en punto territorial
        asignacion_activa = (
            self.db.query(Asignacion)
            .filter(
                Asignacion.contratista_id == contratista_id,
                Asignacion.activa == True,
                Asignacion.es_buffer_movil == False
            )
            .first()
        )

        if not asignacion_activa:
            raise ValueError(f"El contratista {contratista_baja.nombre} no tiene una asignacion en terreno activa.")

        # 2. Localizar un relevo disponible en el buffer movil
        asignacion_reemplazo = (
            self.db.query(Asignacion)
            .filter(
                Asignacion.es_buffer_movil == True,
                Asignacion.activa == True,
                Asignacion.inicio == asignacion_activa.inicio,
                Asignacion.fin == asignacion_activa.fin
            )
            .first()
        )

        if not asignacion_reemplazo:
            raise RuntimeError("ALERTA CRITICA: Buffer movil agotado. No hay personal de reserva disponible.")

        contratista_reemplazo = asignacion_reemplazo.contratista

        # 3. Actualizar estados y ejecutar el relevo de forma atomica
        contratista_baja.estado = EstadoContratista.NOVEDAD
        
        # El relevo toma el punto operativo y sale del buffer flotante
        asignacion_reemplazo.punto_id = asignacion_activa.punto_id
        asignacion_reemplazo.es_buffer_movil = False

        # Desactivar la asignacion del contratista saliente
        asignacion_activa.activa = False

        # 4. Registrar auditoria en tabla Novedades
        registro_novedad = Novedad(
            asignacion_id=asignacion_activa.id,
            tipo=tipo_novedad,
            reemplazo_id=contratista_reemplazo.id,
            detalle=detalle or f"Sustitucion automatica por {tipo_novedad.value}",
            registrado_el=datetime.utcnow()
        )

        self.db.add(registro_novedad)
        self.db.commit()

        return {
            "punto_afectado_id": asignacion_reemplazo.punto_id,
            "contratista_saliente": contratista_baja.nombre,
            "tipo_novedad": tipo_novedad.value,
            "reemplazo_asignado": contratista_reemplazo.nombre,
            "novedad_id": registro_novedad.id
        }


def test_contingency():
    db = SessionLocal()
    try:
        service = ContingencyService(db)
        
        # Tomar el primer contratista asignado a terreno para simular la baja
        asignacion_terreno = (
            db.query(Asignacion)
            .filter(Asignacion.es_buffer_movil == False, Asignacion.activa == True)
            .first()
        )

        if not asignacion_terreno:
            print("No hay asignaciones en terreno para probar contingencias. Ejecuta allocation primero.")
            return

        resultado = service.registrar_baja_y_reemplazar(
            contratista_id=asignacion_terreno.contratista_id,
            tipo_novedad=TipoNovedad.INCAPACIDAD,
            detalle="Incapacidad medica general de 2 dias radicada en campo."
        )

        print("Contingencia resuelta exitosamente:")
        for k, v in resultado.items():
            print(f"  - {k}: {v}")

    finally:
        db.close()


if __name__ == "__main__":
    test_contingency()