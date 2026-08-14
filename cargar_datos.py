import pandas as pd
import mysql.connector
from datetime import datetime
import os
from dotenv import load_dotenv
load_dotenv()

# ============================================
# CONFIGURACIÓN
# ============================================
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': os.getenv('DB_PASSWORD', ''),
    'database': 'sistema_accidentes',
    'charset': 'utf8mb4'
}

ARCHIVO = r'C:\Users\fabia\Desktop\Fabian Incca\2026-2C\OPCIÓN DE GRADO\SistemaAccidentesMoto_BD\historico_siniestros_bogota_d.c'

# ============================================
# MAPEO DE VALORES
# ============================================
GRAVEDAD_MAP = {
    'CON MUERTOS': 'Fatal',
    'CON HERIDOS': 'Herido',
    'SOLO DANOS': 'Solo daños'
}

TIPO_MAP = {
    'CHOQUE': 'Colisión',
    'ATROPELLO': 'Atropello',
    'VOLCAMIENTO': 'Volcamiento',
    'CAIDA DE OCUPANTE': 'Caída de ocupante',
    'AUTOLESION': 'Autolesión',
    'INCENDIO': 'Incendio',
    'OTRO': 'Otro'
}

def cargar_datos():
    print("Leyendo archivo CSV...")
    df = pd.read_csv(ARCHIVO, encoding='utf-8-sig')
    print(f"Total registros en el archivo: {len(df)}")

    # Limpiar y transformar
    df['GRAVEDAD'] = df['GRAVEDAD'].map(GRAVEDAD_MAP).fillna('Herido')
    df['CLASE_ACC'] = df['CLASE_ACC'].map(TIPO_MAP).fillna('Otro')
    df['LOCALIDAD'] = df['LOCALIDAD'].fillna('Sin localidad').str.title()
    df['FECHA_OCURRENCIA_ACC'] = pd.to_datetime(
        df['FECHA_OCURRENCIA_ACC'], errors='coerce', utc=True
    ).dt.date
    df['FECHA_HORA_ACC'] = pd.to_datetime(
        df['FECHA_HORA_ACC'], errors='coerce', utc=True
    )
    df['hora'] = df['FECHA_HORA_ACC'].dt.time
    df['dia_semana'] = pd.to_datetime(
        df['FECHA_OCURRENCIA_ACC'], errors='coerce'
    ).dt.day_name()

    dias_es = {
        'Monday':'Lunes','Tuesday':'Martes','Wednesday':'Miércoles',
        'Thursday':'Jueves','Friday':'Viernes','Saturday':'Sábado','Sunday':'Domingo'
    }
    df['dia_semana'] = df['dia_semana'].map(dias_es).fillna('Lunes')

    # Filtrar solo filas con fecha válida
    df = df.dropna(subset=['FECHA_OCURRENCIA_ACC'])
    print(f"Registros válidos para cargar: {len(df)}")

    # Conectar a MySQL
    print("Conectando a MySQL...")
    db = mysql.connector.connect(**DB_CONFIG)
    cursor = db.cursor()

    # Limpiar datos anteriores de prueba
    print("Limpiando datos de prueba anteriores...")
    cursor.execute("DELETE FROM arbol_causas")
    cursor.execute("DELETE FROM factor_causal")
    cursor.execute("DELETE FROM encuesta_emocional")
    cursor.execute("DELETE FROM siniestro")
    cursor.execute("ALTER TABLE siniestro AUTO_INCREMENT = 1")
    db.commit()

    # Insertar en lotes de 1000
    print("Cargando datos reales...")
    total = len(df)
    lote = 1000
    insertados = 0

    sql = """
        INSERT INTO siniestro 
        (fecha, hora, dia_semana, localidad, zona, tipo_siniestro, 
         causa_oficial, gravedad, actor_vial, condicion_via, 
         condicion_climatica, fuente)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """

    for i in range(0, total, lote):
        chunk = df.iloc[i:i+lote]
        valores = []
        for _, row in chunk.iterrows():
            valores.append((
                row['FECHA_OCURRENCIA_ACC'],
                row['hora'],
                row['dia_semana'],
                str(row['LOCALIDAD'])[:100],
                'Bogotá D.C.',
                str(row['CLASE_ACC'])[:100],
                'Registrado por IPAT',
                str(row['GRAVEDAD'])[:50],
                'Motociclista',
                'No registrada',
                'No registrada',
                'SIGAT - Secretaría de Movilidad Bogotá'
            ))
        cursor.executemany(sql, valores)
        db.commit()
        insertados += len(chunk)
        print(f"  Progreso: {insertados}/{total} ({round(insertados/total*100)}%)")

    cursor.close()
    db.close()
    print(f"\nCarga completada: {insertados} registros insertados en MySQL")
    

if __name__ == '__main__':
    cargar_datos()
