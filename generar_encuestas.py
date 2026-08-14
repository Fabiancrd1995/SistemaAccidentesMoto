import mysql.connector
import random
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

# ============================================
# DATOS PARA GENERAR ENCUESTAS REALISTAS
# ============================================
SITUACIONES = [
    "Discusión con jefe antes de salir del trabajo",
    "Problema económico grave, deudas pendientes",
    "Discusión familiar en la mañana",
    "Presión laboral excesiva, entregas pendientes",
    "Conflicto con compañero de trabajo",
    "Noticia negativa recibida ese día",
    "Problemas de salud propios o familiar",
    "Situación de separación o conflicto sentimental",
    "Pérdida de trabajo o reducción de ingresos",
    "Accidente previo sin reportar ese mismo día",
]

TRAFICOS = ['fluido', 'moderado', 'congestionado', 'muy_congestionado']

# Perfiles emocionales basados en investigación real
# Perfil 1: Alto estrés + ira (mayor riesgo)
# Perfil 2: Fatiga (jornada larga, poco sueño)
# Perfil 3: Tráfico como detonante
# Perfil 4: Sin factores críticos (control)

PERFILES = [
    # (estres, ira, ansiedad, fatiga, sueno, jornada, trafico, situacion)
    # Perfil 1: Alto estrés e ira - 25 encuestas
    {'estres':5,'ira':5,'ansiedad':4,'fatiga':4,'sueno':4.0,'jornada':11,'trafico':'congestionado','situacion':True},
    {'estres':5,'ira':4,'ansiedad':4,'fatiga':3,'sueno':4.5,'jornada':10,'trafico':'congestionado','situacion':True},
    {'estres':4,'ira':5,'ansiedad':3,'fatiga':4,'sueno':5.0,'jornada':10,'trafico':'muy_congestionado','situacion':True},
    {'estres':5,'ira':5,'ansiedad':5,'fatiga':5,'sueno':3.0,'jornada':12,'trafico':'congestionado','situacion':True},
    {'estres':4,'ira':4,'ansiedad':4,'fatiga':3,'sueno':5.5,'jornada':9,'trafico':'congestionado','situacion':True},
    {'estres':5,'ira':5,'ansiedad':3,'fatiga':4,'sueno':4.0,'jornada':11,'trafico':'muy_congestionado','situacion':True},
    {'estres':4,'ira':5,'ansiedad':4,'fatiga':4,'sueno':4.5,'jornada':10,'trafico':'congestionado','situacion':True},
    {'estres':5,'ira':4,'ansiedad':5,'fatiga':3,'sueno':5.0,'jornada':11,'trafico':'congestionado','situacion':True},
    {'estres':5,'ira':5,'ansiedad':4,'fatiga':5,'sueno':3.5,'jornada':13,'trafico':'muy_congestionado','situacion':True},
    {'estres':4,'ira':4,'ansiedad':3,'fatiga':4,'sueno':5.0,'jornada':10,'trafico':'congestionado','situacion':False},
    {'estres':5,'ira':5,'ansiedad':5,'fatiga':4,'sueno':4.0,'jornada':11,'trafico':'congestionado','situacion':True},
    {'estres':4,'ira':5,'ansiedad':4,'fatiga':3,'sueno':5.5,'jornada':9,'trafico':'muy_congestionado','situacion':True},
    {'estres':5,'ira':4,'ansiedad':4,'fatiga':4,'sueno':4.5,'jornada':10,'trafico':'congestionado','situacion':True},
    {'estres':5,'ira':5,'ansiedad':3,'fatiga':5,'sueno':3.0,'jornada':12,'trafico':'congestionado','situacion':True},
    {'estres':4,'ira':4,'ansiedad':4,'fatiga':4,'sueno':5.0,'jornada':10,'trafico':'moderado','situacion':False},
    {'estres':5,'ira':5,'ansiedad':4,'fatiga':3,'sueno':5.0,'jornada':11,'trafico':'congestionado','situacion':True},
    {'estres':4,'ira':5,'ansiedad':5,'fatiga':4,'sueno':4.0,'jornada':10,'trafico':'muy_congestionado','situacion':True},
    {'estres':5,'ira':4,'ansiedad':4,'fatiga':5,'sueno':3.5,'jornada':12,'trafico':'congestionado','situacion':True},
    {'estres':5,'ira':5,'ansiedad':3,'fatiga':4,'sueno':4.5,'jornada':11,'trafico':'congestionado','situacion':True},
    {'estres':4,'ira':4,'ansiedad':4,'fatiga':3,'sueno':5.5,'jornada':9,'trafico':'moderado','situacion':False},
    {'estres':5,'ira':5,'ansiedad':5,'fatiga':4,'sueno':3.0,'jornada':13,'trafico':'muy_congestionado','situacion':True},
    {'estres':4,'ira':5,'ansiedad':4,'fatiga':4,'sueno':4.0,'jornada':10,'trafico':'congestionado','situacion':True},
    {'estres':5,'ira':4,'ansiedad':3,'fatiga':5,'sueno':3.5,'jornada':12,'trafico':'congestionado','situacion':True},
    {'estres':5,'ira':5,'ansiedad':4,'fatiga':4,'sueno':4.5,'jornada':11,'trafico':'muy_congestionado','situacion':True},
    {'estres':4,'ira':4,'ansiedad':4,'fatiga':3,'sueno':5.0,'jornada':9,'trafico':'congestionado','situacion':False},
    # Perfil 2: Fatiga y poco sueño - 20 encuestas
    {'estres':3,'ira':2,'ansiedad':3,'fatiga':5,'sueno':3.0,'jornada':14,'trafico':'moderado','situacion':False},
    {'estres':2,'ira':2,'ansiedad':2,'fatiga':5,'sueno':2.5,'jornada':13,'trafico':'fluido','situacion':False},
    {'estres':3,'ira':3,'ansiedad':2,'fatiga':4,'sueno':4.0,'jornada':12,'trafico':'moderado','situacion':False},
    {'estres':2,'ira':2,'ansiedad':3,'fatiga':5,'sueno':3.5,'jornada':13,'trafico':'fluido','situacion':False},
    {'estres':3,'ira':2,'ansiedad':2,'fatiga':4,'sueno':4.0,'jornada':11,'trafico':'moderado','situacion':False},
    {'estres':2,'ira':3,'ansiedad':3,'fatiga':5,'sueno':3.0,'jornada':14,'trafico':'fluido','situacion':False},
    {'estres':3,'ira':2,'ansiedad':2,'fatiga':5,'sueno':2.5,'jornada':13,'trafico':'moderado','situacion':False},
    {'estres':2,'ira':2,'ansiedad':3,'fatiga':4,'sueno':4.0,'jornada':12,'trafico':'fluido','situacion':False},
    {'estres':3,'ira':3,'ansiedad':2,'fatiga':5,'sueno':3.5,'jornada':13,'trafico':'moderado','situacion':False},
    {'estres':2,'ira':2,'ansiedad':2,'fatiga':4,'sueno':4.0,'jornada':11,'trafico':'fluido','situacion':False},
    {'estres':3,'ira':2,'ansiedad':3,'fatiga':5,'sueno':3.0,'jornada':14,'trafico':'moderado','situacion':False},
    {'estres':2,'ira':3,'ansiedad':2,'fatiga':4,'sueno':4.5,'jornada':12,'trafico':'fluido','situacion':False},
    {'estres':3,'ira':2,'ansiedad':3,'fatiga':5,'sueno':2.5,'jornada':13,'trafico':'moderado','situacion':False},
    {'estres':2,'ira':2,'ansiedad':2,'fatiga':5,'sueno':3.0,'jornada':14,'trafico':'fluido','situacion':False},
    {'estres':3,'ira':3,'ansiedad':3,'fatiga':4,'sueno':4.0,'jornada':11,'trafico':'moderado','situacion':False},
    {'estres':2,'ira':2,'ansiedad':2,'fatiga':5,'sueno':3.5,'jornada':13,'trafico':'fluido','situacion':False},
    {'estres':3,'ira':2,'ansiedad':3,'fatiga':4,'sueno':4.0,'jornada':12,'trafico':'moderado','situacion':False},
    {'estres':2,'ira':3,'ansiedad':2,'fatiga':5,'sueno':2.5,'jornada':14,'trafico':'fluido','situacion':False},
    {'estres':3,'ira':2,'ansiedad':3,'fatiga':4,'sueno':4.0,'jornada':11,'trafico':'moderado','situacion':False},
    {'estres':2,'ira':2,'ansiedad':2,'fatiga':5,'sueno':3.0,'jornada':13,'trafico':'fluido','situacion':False},
    # Perfil 3: Tráfico como detonante - 10 encuestas
    {'estres':4,'ira':4,'ansiedad':3,'fatiga':2,'sueno':7.0,'jornada':8,'trafico':'muy_congestionado','situacion':False},
    {'estres':3,'ira':4,'ansiedad':3,'fatiga':2,'sueno':7.5,'jornada':7,'trafico':'muy_congestionado','situacion':False},
    {'estres':4,'ira':3,'ansiedad':3,'fatiga':2,'sueno':7.0,'jornada':8,'trafico':'congestionado','situacion':False},
    {'estres':3,'ira':4,'ansiedad':2,'fatiga':2,'sueno':8.0,'jornada':7,'trafico':'muy_congestionado','situacion':False},
    {'estres':4,'ira':4,'ansiedad':3,'fatiga':2,'sueno':7.5,'jornada':8,'trafico':'congestionado','situacion':False},
    {'estres':3,'ira':3,'ansiedad':3,'fatiga':2,'sueno':7.0,'jornada':7,'trafico':'muy_congestionado','situacion':False},
    {'estres':4,'ira':4,'ansiedad':2,'fatiga':2,'sueno':8.0,'jornada':8,'trafico':'congestionado','situacion':False},
    {'estres':3,'ira':4,'ansiedad':3,'fatiga':2,'sueno':7.5,'jornada':7,'trafico':'muy_congestionado','situacion':False},
    {'estres':4,'ira':3,'ansiedad':3,'fatiga':2,'sueno':7.0,'jornada':8,'trafico':'congestionado','situacion':False},
    {'estres':3,'ira':4,'ansiedad':2,'fatiga':2,'sueno':8.0,'jornada':7,'trafico':'muy_congestionado','situacion':False},
    # Perfil 4: Sin factores críticos (grupo control) - 5 encuestas
    {'estres':2,'ira':1,'ansiedad':1,'fatiga':2,'sueno':8.0,'jornada':6,'trafico':'fluido','situacion':False},
    {'estres':1,'ira':1,'ansiedad':2,'fatiga':1,'sueno':8.5,'jornada':6,'trafico':'fluido','situacion':False},
    {'estres':2,'ira':2,'ansiedad':1,'fatiga':2,'sueno':8.0,'jornada':7,'trafico':'moderado','situacion':False},
    {'estres':1,'ira':1,'ansiedad':1,'fatiga':1,'sueno':9.0,'jornada':6,'trafico':'fluido','situacion':False},
    {'estres':2,'ira':1,'ansiedad':2,'fatiga':2,'sueno':8.0,'jornada':7,'trafico':'moderado','situacion':False},
]

def generar_encuestas():
    print("Conectando a MySQL...")
    db = mysql.connector.connect(**DB_CONFIG)
    cursor = db.cursor()

    # Obtener IDs de siniestros reales aleatorios
    cursor.execute("SELECT id FROM siniestro ORDER BY RAND() LIMIT 60")
    ids = [row[0] for row in cursor.fetchall()]
    print(f"IDs de siniestros seleccionados: {len(ids)}")

    sql = """
        INSERT INTO encuesta_emocional
        (siniestro_id, tipo_reporte, nivel_estres, nivel_ira, nivel_ansiedad,
         nivel_fatiga, horas_sueno, horas_jornada, condicion_trafico,
         situacion_personal_adversa, descripcion_situacion)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """

    insertadas = 0
    for i, perfil in enumerate(PERFILES):
        siniestro_id = ids[i] if i < len(ids) else None
        situacion_desc = random.choice(SITUACIONES) if perfil['situacion'] else None

        cursor.execute(sql, (
            siniestro_id,
            'post_accidente',
            perfil['estres'],
            perfil['ira'],
            perfil['ansiedad'],
            perfil['fatiga'],
            perfil['sueno'],
            perfil['jornada'],
            perfil['trafico'],
            1 if perfil['situacion'] else 0,
            situacion_desc
        ))
        insertadas += 1

    db.commit()
    cursor.close()
    db.close()

    print(f"\n{insertadas} encuestas piloto generadas exitosamente")
    print("\nDistribución:")
    print("  - Perfil 1 (Alto estrés/ira): 25 encuestas")
    print("  - Perfil 2 (Fatiga/poco sueño): 20 encuestas")
    print("  - Perfil 3 (Tráfico detonante): 10 encuestas")
    print("  - Perfil 4 (Sin factores críticos): 5 encuestas")

if __name__ == '__main__':
    generar_encuestas()
