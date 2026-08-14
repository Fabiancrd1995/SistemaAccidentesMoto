# 🔍 Sistema de Análisis de Causa Raíz para Accidentes de Tránsito
### Énfasis en Motociclistas — Colombia

> Proyecto de Grado · Ingeniería de Sistemas · Universidad INCCA de Colombia · 2026

---

## 📋 Descripción

Sistema de información mixto (investigativo + tecnológico) que integra **bases de datos institucionales de accidentalidad vial** con **encuestas digitales de estado emocional**, con el propósito de identificar y analizar la cadena de causas raíz de los accidentes de tránsito en motociclistas en Colombia.

Los sistemas actuales (ANSV, INMLCF, SIGAT) registran únicamente la causa inmediata del siniestro —como el exceso de velocidad— sin indagar en los factores emocionales y contextuales que lo desencadenaron. Este proyecto cierra esa brecha.

---

## 🎯 Problema que resuelve

| Situación actual | Lo que hace este sistema |
|---|---|
| Solo se registra la causa inmediata (exceso de velocidad) | Identifica la cadena completa de causas |
| No se captura el estado emocional del conductor | Encuesta digital de estrés, ira, fatiga y ansiedad |
| El análisis causal es manual y no sistemático | Motor automatizado de árbol de causas en Python |
| Los datos institucionales están fragmentados | Base de datos MySQL unificada con 199.146 registros reales |

---

## 🖥️ Capturas del Sistema

### Pantalla de Inicio
- 199.146 registros reales de siniestros viales de Bogotá (SIGAT 2015–2021)
- 3.239 casos fatales registrados
- 60 encuestas emocionales piloto

### Árbol de Causas
El sistema genera automáticamente la cadena causal:
```
⚠️ Causa inmediata   →  Registrado por IPAT
        ↓
😤 Causa intermedia  →  Estado emocional alterado (Estrés: 4/5, Ira: 4/5)
        ↓
🔍 Causa raíz        →  Presión laboral excesiva / Jornada de 11 horas
```

### Dashboard Interactivo
- Siniestros por localidad (Kennedy lidera con ~23k casos)
- Distribución por gravedad y franja horaria
- Radar de perfil emocional promedio de conductores

---

## 🛠️ Tecnologías Utilizadas

| Categoría | Tecnología |
|---|---|
| Lenguaje backend | Python 3.x |
| Base de datos | MySQL |
| Framework web | Flask |
| Visualización | Plotly |
| Análisis de datos | Pandas / NumPy |
| Control de versiones | Git / GitHub |
| Apoyo en código | Claude (Anthropic) |

---

## 📦 Instalación y Ejecución

### Requisitos previos
- Python 3.x instalado
- MySQL instalado y corriendo
- Git instalado

### Paso 1 — Clonar el repositorio
```bash
git clone https://github.com/Fabiancrd1995/SistemaAccidentesMoto.git
cd SistemaAccidentesMoto
```

### Paso 2 — Instalar dependencias
```bash
pip install flask mysql-connector-python pandas plotly requests openpyxl python-dotenv
```

### Paso 3 — Configurar variables de entorno
Crea un archivo `.env` en la raíz del proyecto:
```
DB_PASSWORD=TuContraseñaMySQL
```

### Paso 4 — Crear la base de datos
Abre MySQL Workbench y ejecuta el script:
```bash
crear_bd.sql
```

### Paso 5 — Cargar datos reales (opcional)
Descarga el dataset histórico de siniestros de Bogotá desde:
[Datos Abiertos Bogotá](https://datosabiertos.bogota.gov.co/dataset/siniestros-viales-consolidados-bogota-d-c)

Luego ejecuta:
```bash
python cargar_datos.py
```

### Paso 6 — Generar encuestas piloto (opcional)
```bash
python generar_encuestas.py
```

### Paso 7 — Ejecutar la aplicación
```bash
python app.py
```

Abre el navegador en: **http://127.0.0.1:5000**

---

## 📁 Estructura del Proyecto

```
SistemaAccidentesMoto/
├── app.py                  # Aplicación Flask principal + motor de árbol de causas
├── crear_bd.sql            # Script SQL para crear la base de datos MySQL
├── cargar_datos.py         # Carga masiva de datos reales del SIGAT Bogotá
├── generar_encuestas.py    # Generación de encuestas piloto con perfiles emocionales
├── .gitignore              # Archivos excluidos del repositorio
├── .env                    # Variables de entorno (NO subir a GitHub)
└── templates/
    ├── base.html           # Plantilla base con navbar y estilos
    ├── index.html          # Pantalla de inicio con tabla de siniestros
    ├── encuesta.html       # Formulario de encuesta emocional
    ├── arbol.html          # Visualización del árbol de causas raíz
    └── dashboard.html      # Dashboard interactivo de patrones
```

---

## 🗄️ Fuentes de Datos

| Fuente | Descripción | Registros |
|---|---|---|
| SIGAT — Secretaría de Movilidad Bogotá | Siniestros viales 2015–2021 | 199.146 |
| ANSV — Observatorio Nacional de Seguridad Vial | Estadísticas nacionales | Referencia |
| INMLCF — FORENSIS | Víctimas fatales viales | Referencia |
| Encuestas piloto propias | Estado emocional conductores | 60 |

---

## 🌳 Motor de Árbol de Causas

El sistema implementa la metodología de **árbol de causas** y **5 porqués** de forma automatizada:

- **Nivel 1 — Causa inmediata:** dato registrado en el IPAT (exceso de velocidad, atropello, etc.)
- **Nivel 2 — Causa intermedia:** estado emocional del conductor (estrés, ira, fatiga)
- **Nivel 3 — Causa raíz:** factor desencadenante profundo (jornada extensa, situación personal adversa, tráfico congestionado)

---

## 📊 Hallazgos Preliminares

Con base en los 199.146 registros reales y 60 encuestas piloto:

- **Kennedy** es la localidad con mayor accidentalidad (~23.000 casos)
- La **tarde (12–17h)** es la franja horaria de mayor riesgo (~70.000 casos)
- **Estrés promedio:** 3.5/5 · **Ira promedio:** 3.4/5 · **Fatiga promedio:** 3.6/5
- **3.239 casos fatales** registrados en la base de datos real

---

## 👤 Autor

**Fabian Camilo Rodriguez Diaz**  
Ingeniería de Sistemas — Universidad INCCA de Colombia  
Docente: Julieth Carolina Ríos Bocanegra  
Bogotá D.C. · 2026

---

## 📚 Referencias Principales

- Pabón, M. A. (2014). Caracterización de la accidentalidad en Colombia: factor humano. Universidad Nacional de Colombia.
- Santos, K. et al. (2024). Analysis of Motorcycle Accident Injury Severity — ML Algorithms. *Accident Analysis & Prevention.*
- ANSV (2024). Anuario de Siniestralidad Vial de Colombia 2023.
- Secretaría Distrital de Movilidad (2026). SIGAT — Sistema de Información Geográfico de Accidentes de Tránsito.

---

*Proyecto desarrollado con apoyo de Claude (Anthropic) para generación y depuración de código.*
