# app/models/veterinaria.py
from sqlalchemy import Column, Integer, String, DateTime, Text, DECIMAL, Boolean, Date, CHAR, Enum as SQLEnum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship

Base = declarative_base()


class TipoServicio(Base):
    __tablename__ = "Tipo_servicio"

    id_tipo_servicio = Column(Integer, primary_key=True, autoincrement=True)
    descripcion = Column(String(50), nullable=False)

    # Relationships
    servicios = relationship("Servicio", back_populates="tipo_servicio")


class Especialidad(Base):
    __tablename__ = "Especialidad"

    id_especialidad = Column(Integer, primary_key=True, autoincrement=True)
    descripcion = Column(String(50), nullable=False)

    # Relationships
    veterinarios = relationship("Veterinario", back_populates="especialidad")


class Raza(Base):
    __tablename__ = "Raza"

    id_raza = Column(Integer, primary_key=True, autoincrement=True)
    nombre_raza = Column(String(60), nullable=False)

    # Relationships
    tipos_animal = relationship("TipoAnimal", back_populates="raza")
    mascotas = relationship("Mascota", back_populates="raza")


class TipoAnimal(Base):
    __tablename__ = "Tipo_animal"

    id_tipo_animal = Column(Integer, primary_key=True, autoincrement=True)
    id_raza = Column(Integer, ForeignKey('Raza.id_raza'), nullable=False)
    descripcion = Column(SQLEnum('Perro', 'Gato', name='tipo_animal_enum'), nullable=False)

    # Relationships
    raza = relationship("Raza", back_populates="tipos_animal")


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

    # Relationships
    mascotas = relationship("Mascota", back_populates="cliente")
    cliente_mascotas = relationship("ClienteMascota", back_populates="cliente")


class Recepcionista(Base):
    __tablename__ = "Recepcionista"

    id_recepcionista = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String(50), nullable=False)
    apellido_paterno = Column(String(50), nullable=False)
    apellido_materno = Column(String(50), nullable=False)
    dni = Column(CHAR(8), unique=True, nullable=False)
    telefono = Column(CHAR(9), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    fecha_ingreso = Column(Date)
    turno = Column(SQLEnum('Mañana', 'Tarde', 'Noche', name='turno_recepcionista_enum'))
    estado = Column(SQLEnum('Activo', 'Inactivo', name='estado_recepcionista_enum'))
    contraseña = Column(String(50), nullable=False)
    genero = Column(CHAR(1), nullable=False)

    # Relationships
    solicitudes_atencion = relationship("SolicitudAtencion", back_populates="recepcionista")


class Mascota(Base):
    __tablename__ = "Mascota"

    id_mascota = Column(Integer, primary_key=True, autoincrement=True)
    id_cliente = Column(Integer, ForeignKey('Cliente.id_cliente'), nullable=False)
    id_raza = Column(Integer, ForeignKey('Raza.id_raza'), nullable=False)
    nombre = Column(String(50), nullable=False)
    sexo = Column(SQLEnum('Macho', 'Hembra', name='sexo_mascota_enum'), nullable=False)
    color = Column(String(50))
    edad_anios = Column(Integer)
    edad_meses = Column(Integer)
    esterilizado = Column(Boolean, default=False)
    imagen = Column(String(50))

    # Relationships
    cliente = relationship("Cliente", back_populates="mascotas")
    raza = relationship("Raza", back_populates="mascotas")
    solicitudes_atencion = relationship("SolicitudAtencion", back_populates="mascota")
    citas = relationship("Cita", back_populates="mascota")
    historiales_clinicos = relationship("HistorialClinico", back_populates="mascota")
    cliente_mascotas = relationship("ClienteMascota", back_populates="mascota")


class Servicio(Base):
    __tablename__ = "Servicio"

    id_servicio = Column(Integer, primary_key=True, autoincrement=True)
    id_tipo_servicio = Column(Integer, ForeignKey('Tipo_servicio.id_tipo_servicio'), nullable=False)
    nombre_servicio = Column(String(50), nullable=False)
    precio = Column(DECIMAL(6, 2), nullable=False)
    activo = Column(Boolean, default=True)

    # Relationships
    tipo_servicio = relationship("TipoServicio", back_populates="servicios")
    servicios_solicitados = relationship("ServicioSolicitado", back_populates="servicio")
    citas = relationship("Cita", back_populates="servicio")


class Veterinario(Base):
    __tablename__ = "Veterinario"

    id_veterinario = Column(Integer, primary_key=True, autoincrement=True)
    id_especialidad = Column(Integer, ForeignKey('Especialidad.id_especialidad'), nullable=False)
    codigo_CMVP = Column(String(20), nullable=False)
    tipo_veterinario = Column(SQLEnum('Medico General', 'Especializado', name='tipo_veterinario_enum'), nullable=False)
    fecha_nacimiento = Column(Date, nullable=False)
    genero = Column(CHAR(1), nullable=False)
    nombre = Column(String(50), nullable=False)
    apellido_paterno = Column(String(50), nullable=False)
    apellido_materno = Column(String(50), nullable=False)
    dni = Column(CHAR(8), unique=True, nullable=False)
    telefono = Column(CHAR(9), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    estado = Column(SQLEnum('Activo', 'Inactivo', name='estado_veterinario_enum'), default='Activo')
    fecha_ingreso = Column(Date, nullable=False)
    disposicion = Column(SQLEnum('Ocupado', 'Libre', name='disposicion_veterinario_enum'), default='Libre')
    turno = Column(SQLEnum('Mañana', 'Tarde', 'Noche', name='turno_veterinario_enum'), nullable=False)
    contraseña = Column(String(60), nullable=False)

    # Relationships
    especialidad = relationship("Especialidad", back_populates="veterinarios")
    triajes = relationship("Triaje", back_populates="veterinario")
    consultas = relationship("Consulta", back_populates="veterinario")
    resultados_servicio = relationship("ResultadoServicio", back_populates="veterinario")
    historiales_clinicos = relationship("HistorialClinico", back_populates="veterinario")


class SolicitudAtencion(Base):
    __tablename__ = "Solicitud_atencion"

    id_solicitud = Column(Integer, primary_key=True, autoincrement=True)
    id_mascota = Column(Integer, ForeignKey('Mascota.id_mascota'))
    id_recepcionista = Column(Integer, ForeignKey('Recepcionista.id_recepcionista'))
    fecha_hora_solicitud = Column(DateTime)
    tipo_solicitud = Column(
        SQLEnum('Consulta urgente', 'Consulta normal', 'Servicio programado', name='tipo_solicitud_enum'),
        nullable=False)
    estado = Column(
        SQLEnum('Pendiente', 'En triaje', 'En atencion', 'Completada', 'Cancelada', name='estado_solicitud_enum'),
        default='Pendiente')

    # Relationships
    mascota = relationship("Mascota", back_populates="solicitudes_atencion")
    recepcionista = relationship("Recepcionista", back_populates="solicitudes_atencion")
    triajes = relationship("Triaje", back_populates="solicitud")


class Triaje(Base):
    __tablename__ = "Triaje"

    id_triaje = Column(Integer, primary_key=True, autoincrement=True)
    id_solicitud = Column(Integer, ForeignKey('Solicitud_atencion.id_solicitud'), nullable=False)
    id_veterinario = Column(Integer, ForeignKey('Veterinario.id_veterinario'), nullable=False)
    fecha_hora_triaje = Column(DateTime, nullable=False)
    peso_mascota = Column(DECIMAL(5, 2), nullable=False)
    latido_por_minuto = Column(Integer, nullable=False)
    frecuencia_respiratoria_rpm = Column(Integer, nullable=False)
    temperatura = Column(DECIMAL(4, 2), nullable=False)
    talla = Column(DECIMAL(5, 2))
    tiempo_capilar = Column(String(50))
    color_mucosas = Column(String(50))
    frecuencia_pulso = Column(Integer, nullable=False)
    porce_deshidratacion = Column(DECIMAL(4, 2))
    condicion_corporal = Column(
        SQLEnum('Muy delgado', 'Delgado', 'Ideal', 'Sobrepeso', 'Obeso', name='condicion_corporal_enum'),
        default='Ideal')
    clasificacion_urgencia = Column(
        SQLEnum('No urgente', 'Poco urgente', 'Urgente', 'Muy urgente', 'Critico', name='urgencia_enum'),
        nullable=False)

    # Relationships
    solicitud = relationship("SolicitudAtencion", back_populates="triajes")
    veterinario = relationship("Veterinario", back_populates="triajes")
    consultas = relationship("Consulta", back_populates="triaje")


class Consulta(Base):
    __tablename__ = "Consulta"

    id_consulta = Column(Integer, primary_key=True, autoincrement=True)
    id_triaje = Column(Integer, ForeignKey('Triaje.id_triaje'), nullable=False)
    id_veterinario = Column(Integer, ForeignKey('Veterinario.id_veterinario'), nullable=False)
    tipo_consulta = Column(String(100), nullable=False)
    fecha_consulta = Column(DateTime, nullable=False)
    motivo_consulta = Column(Text)
    sintomas_observados = Column(Text)
    diagnostico_preliminar = Column(Text)
    observaciones = Column(Text)
    condicion_general = Column(
        SQLEnum('Excelente', 'Buena', 'Regular', 'Mala', 'Critica', name='condicion_general_enum'), nullable=False)
    es_seguimiento = Column(Boolean, default=False)

    # Relationships
    triaje = relationship("Triaje", back_populates="consultas")
    veterinario = relationship("Veterinario", back_populates="consultas")
    servicios_solicitados = relationship("ServicioSolicitado", back_populates="consulta")
    diagnosticos = relationship("Diagnostico", back_populates="consulta")
    tratamientos = relationship("Tratamiento", back_populates="consulta")
    historiales_clinicos = relationship("HistorialClinico", back_populates="consulta")


class ServicioSolicitado(Base):
    __tablename__ = "Servicio_Solicitado"

    id_servicio_solicitado = Column(Integer, primary_key=True, autoincrement=True)
    id_consulta = Column(Integer, ForeignKey('Consulta.id_consulta'))
    id_servicio = Column(Integer, ForeignKey('Servicio.id_servicio'))
    fecha_solicitado = Column(DateTime)
    prioridad = Column(SQLEnum('Urgente', 'Normal', 'Programable', name='prioridad_enum'))
    estado_examen = Column(SQLEnum('Solicitado', 'Citado', 'En proceso', 'Completado', name='estado_examen_enum'),
                           default='Solicitado')
    comentario_opcional = Column(Text)

    # Relationships
    consulta = relationship("Consulta", back_populates="servicios_solicitados")
    servicio = relationship("Servicio", back_populates="servicios_solicitados")
    citas = relationship("Cita", back_populates="servicio_solicitado")


class Cita(Base):
    __tablename__ = "Cita"

    id_cita = Column(Integer, primary_key=True, autoincrement=True)
    id_mascota = Column(Integer, ForeignKey('Mascota.id_mascota'))
    id_servicio = Column(Integer, ForeignKey('Servicio.id_servicio'))
    id_servicio_solicitado = Column(Integer, ForeignKey('Servicio_Solicitado.id_servicio_solicitado'))
    fecha_hora_programada = Column(DateTime, nullable=False)
    estado_cita = Column(SQLEnum('Programada', 'Cancelada', 'Atendida', name='estado_cita_enum'), default='Programada')
    requiere_ayuno = Column(Boolean)
    observaciones = Column(Text)

    # Relationships
    mascota = relationship("Mascota", back_populates="citas")
    servicio = relationship("Servicio", back_populates="citas")
    servicio_solicitado = relationship("ServicioSolicitado", back_populates="citas")
    resultados_servicio = relationship("ResultadoServicio", back_populates="cita")


class ResultadoServicio(Base):
    __tablename__ = "Resultado_servicio"

    id_resultado = Column(Integer, primary_key=True, autoincrement=True)
    id_cita = Column(Integer, ForeignKey('Cita.id_cita'))
    id_veterinario = Column(Integer, ForeignKey('Veterinario.id_veterinario'))
    resultado = Column(Text, nullable=False)
    interpretacion = Column(Text)
    archivo_adjunto = Column(String(100))
    fecha_realizacion = Column(DateTime, nullable=False)

    # Relationships
    cita = relationship("Cita", back_populates="resultados_servicio")
    veterinario = relationship("Veterinario", back_populates="resultados_servicio")


class Patologia(Base):
    __tablename__ = "Patología"

    id_patologia = Column(Integer, primary_key=True, autoincrement=True)
    nombre_patologia = Column(String(100), nullable=False, unique=True)
    especie_afecta = Column(SQLEnum('Perro', 'Gato', 'Ambas', name='especie_afecta_enum'), nullable=False)
    gravedad = Column(SQLEnum('Leve', 'Moderada', 'Grave', 'Critica', name='gravedad_enum'), default='Moderada')
    es_cronica = Column(Boolean)
    es_contagiosa = Column(Boolean)

    # Relationships
    diagnosticos = relationship("Diagnostico", back_populates="patologia")
    tratamientos = relationship("Tratamiento", back_populates="patologia")


class Diagnostico(Base):
    __tablename__ = "Diagnostico"

    id_diagnostico = Column(Integer, primary_key=True, autoincrement=True)
    id_consulta = Column(Integer, ForeignKey('Consulta.id_consulta'))
    id_patologia = Column(Integer, ForeignKey('Patología.id_patología'))
    tipo_diagnostico = Column(SQLEnum('Presuntivo', 'Confirmado', 'Descartado', name='tipo_diagnostico_enum'),
                              nullable=False, default='Presuntivo')
    fecha_diagnostico = Column(DateTime, nullable=False)
    estado_patologia = Column(SQLEnum('Activa', 'Controlada', 'Curada', 'En seguimiento', name='estado_patologia_enum'),
                              nullable=False, default='Activa')
    diagnostico = Column(Text, nullable=False)

    # Relationships
    consulta = relationship("Consulta", back_populates="diagnosticos")
    patologia = relationship("Patologia", back_populates="diagnosticos")
    historiales_clinicos = relationship("HistorialClinico", back_populates="diagnostico")


class Tratamiento(Base):
    __tablename__ = "Tratamiento"

    id_tratamiento = Column(Integer, primary_key=True, autoincrement=True)
    id_consulta = Column(Integer, ForeignKey('Consulta.id_consulta'))
    id_patologia = Column(Integer, ForeignKey('Patología.id_patología'))
    fecha_inicio = Column(Date, nullable=False)
    eficacia_tratamiento = Column(SQLEnum('Muy buena', 'Buena', 'Regular', 'Mala', name='eficacia_enum'))
    tipo_tratamiento = Column(
        SQLEnum('Medicamentoso', 'Quirurgico', 'Terapeutico', 'Preventivo', name='tipo_tratamiento_enum'),
        nullable=False)

    # Relationships
    consulta = relationship("Consulta", back_populates="tratamientos")
    patologia = relationship("Patologia", back_populates="tratamientos")
    historiales_clinicos = relationship("HistorialClinico", back_populates="tratamiento")


class HistorialClinico(Base):
    __tablename__ = "Historial_clinico"

    id_historial = Column(Integer, primary_key=True, autoincrement=True)
    id_mascota = Column(Integer, ForeignKey('Mascota.id_mascota'))
    id_consulta = Column(Integer, ForeignKey('Consulta.id_consulta'))
    id_diagnostico = Column(Integer, ForeignKey('Diagnostico.id_diagnostico'))
    id_tratamiento = Column(Integer, ForeignKey('Tratamiento.id_tratamiento'))
    id_veterinario = Column(Integer, ForeignKey('Veterinario.id_veterinario'))
    fecha_evento = Column(DateTime, nullable=False)
    tipo_evento = Column(String(100), nullable=False)
    edad_meses = Column(Integer)
    descripcion_evento = Column(Text, nullable=False)
    peso_momento = Column(DECIMAL(5, 2))
    observaciones = Column(Text)

    # Relationships
    mascota = relationship("Mascota", back_populates="historiales_clinicos")
    consulta = relationship("Consulta", back_populates="historiales_clinicos")
    diagnostico = relationship("Diagnostico", back_populates="historiales_clinicos")
    tratamiento = relationship("Tratamiento", back_populates="historiales_clinicos")
    veterinario = relationship("Veterinario", back_populates="historiales_clinicos")


class ClienteMascota(Base):
    __tablename__ = "Cliente_Mascota"

    id_cliente_mascota = Column(Integer, primary_key=True, autoincrement=True)
    id_cliente = Column(Integer, ForeignKey('Cliente.id_cliente'))
    id_mascota = Column(Integer, ForeignKey('Mascota.id_mascota'))

    # Relationships
    cliente = relationship("Cliente", back_populates="cliente_mascotas")
    mascota = relationship("Mascota", back_populates="cliente_mascotas")