import enum
from datetime import datetime
from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    DateTime,
    ForeignKey,
    Enum as SQLEnum,
    Text,
)
from sqlalchemy.orm import relationship

from src.database.connection import Base


class EstadoContratista(str, enum.Enum):
    DISPONIBLE = "disponible"
    NOVEDAD = "novedad"
    INACTIVO = "inactivo"


class NivelCriticidad(str, enum.Enum):
    BAJA = "baja"
    MEDIA = "media"
    ALTA = "alta"


class TipoNovedad(str, enum.Enum):
    INCAPACIDAD = "incapacidad"
    CALAMIDAD = "calamidad"
    CASO_FORTUITO = "caso_fortuito"
    RETIRO = "retiro"


class Contratista(Base):
    __tablename__ = "contratistas"

    id = Column(Integer, primary_key=True, autoincrement=True)
    documento = Column(String(30), unique=True, nullable=False, index=True)
    nombre = Column(String(120), nullable=False)
    rol = Column(String(80), nullable=False)  # ej: Gestor de Convivencia, Líder Operativo
    estado = Column(
        SQLEnum(EstadoContratista),
        default=EstadoContratista.DISPONIBLE,
        nullable=False,
    )

    # Relaciones
    asignaciones = relationship("Asignacion", back_populates="contratista")

    def __repr__(self):
        return f"<Contratista(id={self.id}, doc='{self.documento}', nombre='{self.nombre}', estado='{self.estado}')>"


class PuntoOperacion(Base):
    __tablename__ = "puntos_operacion"

    id = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String(120), nullable=False, unique=True)
    sector = Column(String(100), nullable=False)  # ej: Polígono Central, Estación X
    criticidad = Column(
        SQLEnum(NivelCriticidad),
        default=NivelCriticidad.MEDIA,
        nullable=False,
    )
    requerimiento_minimo = Column(Integer, default=1, nullable=False)

    # Relaciones
    asignaciones = relationship("Asignacion", back_populates="punto")

    def __repr__(self):
        return f"<PuntoOperacion(id={self.id}, nombre='{self.nombre}', criticidad='{self.criticidad}')>"


class Asignacion(Base):
    __tablename__ = "asignaciones"

    id = Column(Integer, primary_key=True, autoincrement=True)
    contratista_id = Column(Integer, ForeignKey("contratistas.id"), nullable=False, index=True)
    punto_id = Column(Integer, ForeignKey("puntos_operacion.id"), nullable=True, index=True)
    inicio = Column(DateTime, nullable=False)
    fin = Column(DateTime, nullable=False)
    es_buffer_movil = Column(Boolean, default=False, nullable=False)  # True si forma parte del 10%-15% móvil
    activa = Column(Boolean, default=True, nullable=False)

    # Relaciones
    contratista = relationship("Contratista", back_populates="asignaciones")
    punto = relationship("PuntoOperacion", back_populates="asignaciones")
    novedades = relationship("Novedad", back_populates="asignacion")

    def __repr__(self):
        return f"<Asignacion(id={self.id}, contratista_id={self.contratista_id}, punto_id={self.punto_id}, buffer={self.es_buffer_movil})>"


class Novedad(Base):
    __tablename__ = "novedades"

    id = Column(Integer, primary_key=True, autoincrement=True)
    asignacion_id = Column(Integer, ForeignKey("asignaciones.id"), nullable=False, index=True)
    tipo = Column(SQLEnum(TipoNovedad), nullable=False)
    reemplazo_id = Column(Integer, ForeignKey("contratistas.id"), nullable=True)  # Contratista del buffer asignado
    detalle = Column(Text, nullable=True)
    registrado_el = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relaciones
    asignacion = relationship("Asignacion", back_populates="novedades")
    reemplazo = relationship("Contratista", foreign_keys=[reemplazo_id])

    def __repr__(self):
        return f"<Novedad(id={self.id}, tipo='{self.tipo}', asignacion_id={self.asignacion_id}, reemplazo_id={self.reemplazo_id})>"