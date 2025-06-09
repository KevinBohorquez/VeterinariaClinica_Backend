# app/models/mascota.py
from sqlalchemy import Column, Integer, String, Enum as SQLEnum, ForeignKey, Boolean, CheckConstraint
from app.models.base import Base
from sqlalchemy.orm import relationship


class Mascota(Base):
    __tablename__ = "Mascota"

    id_mascota = Column(Integer, primary_key=True, autoincrement=True)
    id_raza = Column(Integer, ForeignKey('Raza.id_raza'), nullable=False)
    
    nombre = Column(String(50), nullable=False)
    sexo = Column(SQLEnum('Macho', 'Hembra', name='sexo_enum'), nullable=False)
    color = Column(String(50))
    edad_anios = Column(Integer)
    edad_meses = Column(Integer)
    esterilizado = Column(Boolean, default=False)
    imagen = Column(String(50))

    raza = relationship("Raza", back_populates="mascotas")
    # Relación many-to-many con Cliente a través de Cliente_Mascota
    clientes = relationship("Cliente", secondary="Cliente_Mascota", back_populates="mascotas")
    # Constraints de validación
    __table_args__ = (
        CheckConstraint("TRIM(nombre) != '' AND LENGTH(TRIM(nombre)) >= 2", name='check_nombre_mascota'),
        CheckConstraint("color IS NULL OR (TRIM(color) != '' AND LENGTH(TRIM(color)) >= 3)", name='check_color_mascota'),
        CheckConstraint("edad_anios IS NULL OR (edad_anios >= 0 AND edad_anios <= 25)", name='check_edad_anios'),
        CheckConstraint("edad_meses IS NULL OR (edad_meses >= 0 AND edad_meses <= 11)", name='check_edad_meses'),
    )