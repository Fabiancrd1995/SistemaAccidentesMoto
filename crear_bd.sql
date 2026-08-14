-- ============================================
-- SISTEMA DE ANÁLISIS DE CAUSA RAÍZ
-- Accidentes de Tránsito - Motociclistas
-- Grupo 7 - Universidad INCCA de Colombia
-- ============================================

CREATE DATABASE IF NOT EXISTS sistema_accidentes
CHARACTER SET utf8mb4 COLLATE utf8mb4_spanish_ci;

USE sistema_accidentes;

-- ============================================
-- TABLA: siniestro
-- Registros de accidentes viales institucionales
-- ============================================
CREATE TABLE IF NOT EXISTS siniestro (
    id INT AUTO_INCREMENT PRIMARY KEY,
    fecha DATE NOT NULL,
    hora TIME,
    dia_semana VARCHAR(20),
    localidad VARCHAR(100),
    zona VARCHAR(100),
    tipo_siniestro VARCHAR(100),
    causa_oficial VARCHAR(200),
    gravedad VARCHAR(50),
    actor_vial VARCHAR(50) DEFAULT 'Motociclista',
    condicion_via VARCHAR(100),
    condicion_climatica VARCHAR(100),
    fuente VARCHAR(100),
    creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- TABLA: encuesta_emocional
-- Estado emocional del conductor pre/post siniestro
-- ============================================
CREATE TABLE IF NOT EXISTS encuesta_emocional (
    id INT AUTO_INCREMENT PRIMARY KEY,
    siniestro_id INT,
    tipo_reporte ENUM('pre_conduccion','post_accidente') NOT NULL,
    nivel_estres TINYINT CHECK (nivel_estres BETWEEN 1 AND 5),
    nivel_ira TINYINT CHECK (nivel_ira BETWEEN 1 AND 5),
    nivel_ansiedad TINYINT CHECK (nivel_ansiedad BETWEEN 1 AND 5),
    nivel_fatiga TINYINT CHECK (nivel_fatiga BETWEEN 1 AND 5),
    horas_sueno DECIMAL(3,1),
    horas_jornada DECIMAL(3,1),
    condicion_trafico ENUM('fluido','moderado','congestionado','muy_congestionado'),
    situacion_personal_adversa BOOLEAN DEFAULT FALSE,
    descripcion_situacion TEXT,
    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (siniestro_id) REFERENCES siniestro(id) ON DELETE SET NULL
);

-- ============================================
-- TABLA: factor_causal
-- Factores identificados en la cadena de causas
-- ============================================
CREATE TABLE IF NOT EXISTS factor_causal (
    id INT AUTO_INCREMENT PRIMARY KEY,
    siniestro_id INT NOT NULL,
    nivel INT NOT NULL COMMENT '1=causa inmediata, 2=causa intermedia, 3=causa raiz',
    descripcion VARCHAR(300) NOT NULL,
    categoria ENUM('humano','ambiental','vehicular','institucional','emocional') NOT NULL,
    es_causa_raiz BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (siniestro_id) REFERENCES siniestro(id) ON DELETE CASCADE
);

-- ============================================
-- TABLA: arbol_causas
-- Árbol de causas generado por el sistema
-- ============================================
CREATE TABLE IF NOT EXISTS arbol_causas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    siniestro_id INT NOT NULL,
    causa_raiz VARCHAR(300),
    resumen_cadena TEXT,
    generado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (siniestro_id) REFERENCES siniestro(id) ON DELETE CASCADE
);

-- ============================================
-- TABLA: usuario
-- Usuarios del sistema
-- ============================================
CREATE TABLE IF NOT EXISTS usuario (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(150) NOT NULL,
    email VARCHAR(150) UNIQUE NOT NULL,
    rol ENUM('administrador','analista','motociclista') NOT NULL,
    password_hash VARCHAR(255),
    activo BOOLEAN DEFAULT TRUE,
    creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- DATOS DE PRUEBA - SINIESTROS
-- Basados en patrones reales ANSV / SIGAT Bogotá
-- ============================================
INSERT INTO siniestro (fecha, hora, dia_semana, localidad, zona, tipo_siniestro, causa_oficial, gravedad, actor_vial, condicion_via, condicion_climatica, fuente) VALUES
('2024-01-15', '07:30:00', 'Lunes', 'Kennedy', 'Sur', 'Colisión', 'Exceso de velocidad', 'Herido', 'Motociclista', 'Seca', 'Despejado', 'SIGAT Bogotá'),
('2024-01-22', '18:45:00', 'Lunes', 'Suba', 'Norte', 'Atropello', 'No respetar señales', 'Herido grave', 'Motociclista', 'Húmeda', 'Lluvia', 'SIGAT Bogotá'),
('2024-02-03', '22:10:00', 'Sábado', 'Bosa', 'Sur', 'Colisión', 'Exceso de velocidad', 'Fatal', 'Motociclista', 'Seca', 'Despejado', 'SIGAT Bogotá'),
('2024-02-14', '06:20:00', 'Miércoles', 'Usaquén', 'Norte', 'Volcamiento', 'Exceso de velocidad', 'Herido', 'Motociclista', 'Húmeda', 'Niebla', 'SIGAT Bogotá'),
('2024-03-05', '12:30:00', 'Martes', 'Fontibón', 'Occidente', 'Colisión', 'Adelantamiento indebido', 'Herido', 'Motociclista', 'Seca', 'Despejado', 'SIGAT Bogotá'),
('2024-03-18', '20:00:00', 'Lunes', 'Rafael Uribe', 'Sur', 'Colisión', 'Exceso de velocidad', 'Fatal', 'Motociclista', 'Seca', 'Despejado', 'SIGAT Bogotá'),
('2024-04-02', '08:15:00', 'Martes', 'Engativá', 'Occidente', 'Atropello', 'No respetar señales', 'Herido grave', 'Motociclista', 'Húmeda', 'Lluvia', 'SIGAT Bogotá'),
('2024-04-20', '17:50:00', 'Sábado', 'Ciudad Bolívar', 'Sur', 'Colisión', 'Exceso de velocidad', 'Herido', 'Motociclista', 'Seca', 'Despejado', 'SIGAT Bogotá'),
('2024-05-07', '23:30:00', 'Martes', 'Chapinero', 'Centro', 'Colisión', 'Embriaguez', 'Fatal', 'Motociclista', 'Seca', 'Despejado', 'SIGAT Bogotá'),
('2024-05-19', '07:00:00', 'Domingo', 'Puente Aranda', 'Occidente', 'Volcamiento', 'Exceso de velocidad', 'Herido', 'Motociclista', 'Húmeda', 'Lluvia', 'SIGAT Bogotá'),
('2024-06-11', '19:20:00', 'Martes', 'Barrios Unidos', 'Norte', 'Colisión', 'Exceso de velocidad', 'Herido grave', 'Motociclista', 'Seca', 'Despejado', 'SIGAT Bogotá'),
('2024-06-25', '14:40:00', 'Martes', 'Teusaquillo', 'Centro', 'Atropello', 'No respetar señales', 'Herido', 'Motociclista', 'Seca', 'Despejado', 'SIGAT Bogotá'),
('2024-07-08', '21:15:00', 'Lunes', 'Kennedy', 'Sur', 'Colisión', 'Exceso de velocidad', 'Fatal', 'Motociclista', 'Seca', 'Despejado', 'SIGAT Bogotá'),
('2024-07-22', '06:45:00', 'Lunes', 'Suba', 'Norte', 'Colisión', 'Exceso de velocidad', 'Herido', 'Motociclista', 'Húmeda', 'Lluvia', 'SIGAT Bogotá'),
('2024-08-14', '18:00:00', 'Miércoles', 'Bosa', 'Sur', 'Colisión', 'Adelantamiento indebido', 'Herido grave', 'Motociclista', 'Seca', 'Despejado', 'SIGAT Bogotá');

-- ============================================
-- DATOS DE PRUEBA - ENCUESTAS EMOCIONALES
-- ============================================
INSERT INTO encuesta_emocional (siniestro_id, tipo_reporte, nivel_estres, nivel_ira, nivel_ansiedad, nivel_fatiga, horas_sueno, horas_jornada, condicion_trafico, situacion_personal_adversa, descripcion_situacion) VALUES
(1, 'post_accidente', 4, 5, 3, 4, 4.5, 10, 'congestionado', TRUE, 'Discusión con jefe antes de salir'),
(2, 'post_accidente', 3, 4, 4, 3, 5.0, 9, 'muy_congestionado', FALSE, NULL),
(3, 'post_accidente', 5, 5, 4, 5, 3.0, 12, 'congestionado', TRUE, 'Problema económico grave'),
(4, 'post_accidente', 2, 2, 3, 4, 6.0, 8, 'moderado', FALSE, NULL),
(5, 'post_accidente', 3, 3, 2, 2, 7.0, 7, 'fluido', FALSE, NULL),
(6, 'post_accidente', 5, 5, 5, 4, 3.5, 11, 'congestionado', TRUE, 'Discusión familiar'),
(7, 'post_accidente', 4, 3, 4, 3, 5.5, 9, 'muy_congestionado', FALSE, NULL),
(8, 'post_accidente', 3, 4, 3, 4, 5.0, 10, 'congestionado', FALSE, NULL),
(9, 'post_accidente', 5, 5, 5, 5, 2.5, 14, 'congestionado', TRUE, 'Deudas y problemas económicos'),
(10, 'post_accidente', 2, 2, 2, 3, 7.5, 6, 'moderado', FALSE, NULL),
(11, 'post_accidente', 4, 5, 3, 4, 4.0, 10, 'congestionado', TRUE, 'Conflicto con compañero de trabajo'),
(12, 'post_accidente', 2, 2, 2, 2, 8.0, 6, 'fluido', FALSE, NULL),
(13, 'post_accidente', 5, 5, 4, 5, 3.0, 13, 'muy_congestionado', TRUE, 'Situación familiar crítica'),
(14, 'post_accidente', 3, 3, 3, 4, 5.0, 8, 'congestionado', FALSE, NULL),
(15, 'post_accidente', 4, 4, 3, 3, 6.0, 9, 'congestionado', TRUE, 'Presión laboral excesiva');

-- ============================================
-- USUARIO ADMINISTRADOR POR DEFECTO
-- ============================================
INSERT INTO usuario (nombre, email, rol, password_hash) VALUES
('Administrador', 'admin@incca.edu.co', 'administrador', 'admin123'),
('Fabian Rodriguez', 'fabian@incca.edu.co', 'analista', 'analista123');

SELECT 'Base de datos creada exitosamente' AS resultado;
SELECT COUNT(*) AS total_siniestros FROM siniestro;
SELECT COUNT(*) AS total_encuestas FROM encuesta_emocional;
