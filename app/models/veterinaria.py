# app/models/veterinaria.py (SOLO CLIENTES - SIN RELACIONES)
from sqlalchemy import Column, Integer, String, DateTime, Text, CHAR, Enum as SQLEnum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()


class Cliente(Base):
    __tablename__ = "Cliente"

    id_cliente = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String(50), nullable=False)
    apellido_paterno = Column(String(50), nullable=False)
    apellido_materno = Column(String(50), nullable=False)
    dni = Column(CHAR(8), unique=True, nullable=False)
    telefono = Column(CHAR(9), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    direccion = Column(Text)
    fecha_registro = Column(DateTime, default=func.current_timestamp())
    estado = Column(SQLEnum('Activo', 'Inactivo', name='estado_cliente_enum'))