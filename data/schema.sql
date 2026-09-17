-- ========================================================
-- DDL: Definicion de Esquema y Relaciones de Base de Datos
-- ========================================================

CREATE TABLE contratistas (
	id INTEGER NOT NULL, 
	documento VARCHAR(30) NOT NULL, 
	nombre VARCHAR(120) NOT NULL, 
	rol VARCHAR(80) NOT NULL, 
	estado VARCHAR(10) NOT NULL, 
	PRIMARY KEY (id)
);

CREATE UNIQUE INDEX ix_contratistas_documento ON contratistas (documento);

CREATE TABLE puntos_operacion (
	id INTEGER NOT NULL, 
	nombre VARCHAR(120) NOT NULL, 
	sector VARCHAR(100) NOT NULL, 
	criticidad VARCHAR(5) NOT NULL, 
	requerimiento_minimo INTEGER NOT NULL, 
	PRIMARY KEY (id), 
	UNIQUE (nombre)
);

CREATE TABLE asignaciones (
	id INTEGER NOT NULL, 
	contratista_id INTEGER NOT NULL, 
	punto_id INTEGER, 
	inicio DATETIME NOT NULL, 
	fin DATETIME NOT NULL, 
	es_buffer_movil BOOLEAN NOT NULL, 
	activa BOOLEAN NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(contratista_id) REFERENCES contratistas (id), 
	FOREIGN KEY(punto_id) REFERENCES puntos_operacion (id)
);

CREATE INDEX ix_asignaciones_punto_id ON asignaciones (punto_id);

CREATE INDEX ix_asignaciones_contratista_id ON asignaciones (contratista_id);

CREATE TABLE novedades (
	id INTEGER NOT NULL, 
	asignacion_id INTEGER NOT NULL, 
	tipo VARCHAR(13) NOT NULL, 
	reemplazo_id INTEGER, 
	detalle TEXT, 
	registrado_el DATETIME NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(asignacion_id) REFERENCES asignaciones (id), 
	FOREIGN KEY(reemplazo_id) REFERENCES contratistas (id)
);

CREATE INDEX ix_novedades_asignacion_id ON novedades (asignacion_id);
