--liquibase formatted sql

--changeset codex:001-create-profesores
CREATE TABLE profesores (
    id BIGSERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    especialidad VARCHAR(100),
    biografia TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

--rollback DROP TABLE IF EXISTS profesores;

--changeset codex:002-create-estudiantes
CREATE TABLE estudiantes (
    id BIGSERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    carrera VARCHAR(100),
    año_ingreso INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

--rollback DROP TABLE IF EXISTS estudiantes;

--changeset codex:003-create-cursos
CREATE TABLE cursos (
    id BIGSERIAL PRIMARY KEY,
    titulo VARCHAR(200) NOT NULL,
    descripcion TEXT,
    profesor_id BIGINT REFERENCES profesores(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

--rollback DROP TABLE IF EXISTS cursos;

--changeset codex:004-create-inscripciones
CREATE TABLE inscripciones (
    id BIGSERIAL PRIMARY KEY,
    estudiante_id BIGINT REFERENCES estudiantes(id) ON DELETE CASCADE,
    curso_id BIGINT REFERENCES cursos(id) ON DELETE CASCADE,
    fecha_inscripcion DATE DEFAULT CURRENT_DATE,
    calificacion NUMERIC(4,2),
    UNIQUE(estudiante_id, curso_id)  -- Evita duplicados
);
--rollback DROP TABLE IF EXISTS inscripciones;
