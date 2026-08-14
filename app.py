from flask import Flask, render_template, request, redirect, url_for, jsonify
import mysql.connector
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import json

app = Flask(__name__)

# ============================================
# 
# http://127.0.0.1:5000
# python app.py
#
# CONFIGURACIÓN DE BASE DE DATOS
# ============================================
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '95100805325F.', # Contraseña de MySQL
    'database': 'sistema_accidentes',
    'charset': 'utf8mb4'
}

def get_db():
    return mysql.connector.connect(**DB_CONFIG)


# ============================================
# MOTOR DE ÁRBOL DE CAUSAS
# ============================================
def generar_arbol_causas(siniestro_id):
    db = get_db()
    cursor = db.cursor(dictionary=True)

    cursor.execute("SELECT * FROM siniestro WHERE id = %s", (siniestro_id,))
    siniestro = cursor.fetchone()

    cursor.execute("SELECT * FROM encuesta_emocional WHERE siniestro_id = %s", (siniestro_id,))
    encuesta = cursor.fetchone()

    if not siniestro:
        return None

    cadena = []
    causa_raiz = ""

    # Nivel 1: Causa inmediata (oficial)
    causa_inmediata = siniestro['causa_oficial']
    cadena.append({
        'nivel': 1,
        'descripcion': causa_inmediata,
        'categoria': 'institucional',
        'label': 'Causa inmediata'
    })

    if encuesta:
        estres = encuesta['nivel_estres'] or 0
        ira = encuesta['nivel_ira'] or 0
        fatiga = encuesta['nivel_fatiga'] or 0
        horas_sueno = encuesta['horas_sueno'] or 8
        horas_jornada = encuesta['horas_jornada'] or 8
        trafico = encuesta['condicion_trafico'] or 'moderado'
        situacion = encuesta['situacion_personal_adversa']

        # Nivel 2: Causa intermedia (estado emocional)
        if ira >= 4 or estres >= 4:
            causa_intermedia = f"Estado emocional alterado (Estrés: {estres}/5, Ira: {ira}/5)"
            cadena.append({
                'nivel': 2,
                'descripcion': causa_intermedia,
                'categoria': 'emocional',
                'label': 'Causa intermedia'
            })

            # Nivel 3: Causa raíz
            if situacion:
                causa_raiz = f"Situación personal adversa: {encuesta.get('descripcion_situacion', 'No especificada')}"
            elif horas_jornada >= 10:
                causa_raiz = f"Jornada laboral extensa ({horas_jornada} horas) que generó agotamiento y estrés"
            elif trafico in ['congestionado', 'muy_congestionado']:
                causa_raiz = f"Tráfico {trafico} que desencadenó ira y conducción agresiva"
            else:
                causa_raiz = "Acumulación de factores de estrés sin causa puntual identificada"

        elif fatiga >= 4 or horas_sueno <= 5:
            causa_intermedia = f"Fatiga al conducir (Fatiga: {fatiga}/5, Horas de sueño: {horas_sueno})"
            cadena.append({
                'nivel': 2,
                'descripcion': causa_intermedia,
                'categoria': 'humano',
                'label': 'Causa intermedia'
            })
            causa_raiz = f"Descanso insuficiente ({horas_sueno} horas de sueño) combinado con jornada de {horas_jornada} horas"

        elif trafico in ['congestionado', 'muy_congestionado']:
            causa_intermedia = f"Condición de tráfico {trafico} que generó impaciencia"
            cadena.append({
                'nivel': 2,
                'descripcion': causa_intermedia,
                'categoria': 'ambiental',
                'label': 'Causa intermedia'
            })
            causa_raiz = "Infraestructura vial insuficiente para el volumen de tráfico en la zona y hora del siniestro"

        else:
            causa_raiz = "Sin factores emocionales o contextuales críticos identificados en la encuesta"

    else:
        causa_raiz = "Sin datos de encuesta emocional — análisis basado únicamente en registro institucional"

    cadena.append({
        'nivel': 3,
        'descripcion': causa_raiz,
        'categoria': 'raiz',
        'label': 'Causa raíz'
    })

    # Guardar en BD
    cursor.execute("DELETE FROM factor_causal WHERE siniestro_id = %s", (siniestro_id,))
    cursor.execute("DELETE FROM arbol_causas WHERE siniestro_id = %s", (siniestro_id,))

    for factor in cadena:
        cursor.execute("""
            INSERT INTO factor_causal (siniestro_id, nivel, descripcion, categoria, es_causa_raiz)
            VALUES (%s, %s, %s, %s, %s)
        """, (siniestro_id, factor['nivel'], factor['descripcion'], factor['categoria'], factor['nivel'] == 3))

    cursor.execute("""
        INSERT INTO arbol_causas (siniestro_id, causa_raiz, resumen_cadena)
        VALUES (%s, %s, %s)
    """, (siniestro_id, causa_raiz, ' → '.join([f['descripcion'] for f in cadena])))

    db.commit()
    cursor.close()
    db.close()

    return {'siniestro': siniestro, 'encuesta': encuesta, 'cadena': cadena, 'causa_raiz': causa_raiz}


# ============================================
# RUTAS
# ============================================

@app.route('/')
def index():
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("""
        SELECT s.*, e.nivel_estres, e.nivel_ira, e.nivel_fatiga
        FROM siniestro s
        LEFT JOIN encuesta_emocional e ON s.id = e.siniestro_id
        ORDER BY s.fecha DESC
    """)
    siniestros = cursor.fetchall()
    cursor.execute("SELECT COUNT(*) as total FROM siniestro")
    total = cursor.fetchone()['total']
    cursor.execute("SELECT COUNT(*) as total FROM siniestro WHERE gravedad = 'Fatal'")
    fatales = cursor.fetchone()['total']
    cursor.execute("SELECT COUNT(*) as total FROM encuesta_emocional")
    encuestas = cursor.fetchone()['total']
    cursor.close()
    db.close()
    return render_template('index.html', siniestros=siniestros, total=total, fatales=fatales, encuestas=encuestas)


@app.route('/encuesta', methods=['GET', 'POST'])
def encuesta():
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT id, fecha, localidad, tipo_siniestro FROM siniestro ORDER BY fecha DESC")
    siniestros = cursor.fetchall()

    if request.method == 'POST':
        datos = request.form
        cursor.execute("""
            INSERT INTO encuesta_emocional
            (siniestro_id, tipo_reporte, nivel_estres, nivel_ira, nivel_ansiedad,
             nivel_fatiga, horas_sueno, horas_jornada, condicion_trafico,
             situacion_personal_adversa, descripcion_situacion)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            datos.get('siniestro_id') or None,
            datos['tipo_reporte'],
            datos['nivel_estres'],
            datos['nivel_ira'],
            datos['nivel_ansiedad'],
            datos['nivel_fatiga'],
            datos['horas_sueno'],
            datos['horas_jornada'],
            datos['condicion_trafico'],
            1 if datos.get('situacion_personal_adversa') else 0,
            datos.get('descripcion_situacion', '')
        ))
        db.commit()
        cursor.close()
        db.close()
        return redirect(url_for('index'))

    cursor.close()
    db.close()
    return render_template('encuesta.html', siniestros=siniestros)


@app.route('/arbol/<int:siniestro_id>')
def arbol(siniestro_id):
    resultado = generar_arbol_causas(siniestro_id)
    if not resultado:
        return "Siniestro no encontrado", 404
    return render_template('arbol.html', resultado=resultado)


@app.route('/dashboard')
def dashboard():
    db = get_db()
    cursor = db.cursor(dictionary=True)

    cursor.execute("""
        SELECT localidad, COUNT(*) as total
        FROM siniestro GROUP BY localidad ORDER BY total DESC
    """)
    por_localidad = cursor.fetchall()

    cursor.execute("""
        SELECT causa_oficial, COUNT(*) as total
        FROM siniestro GROUP BY causa_oficial ORDER BY total DESC
    """)
    por_causa = cursor.fetchall()

    cursor.execute("""
        SELECT gravedad, COUNT(*) as total
        FROM siniestro GROUP BY gravedad
    """)
    por_gravedad = cursor.fetchall()

    cursor.execute("""
        SELECT
            CASE
                WHEN HOUR(hora) BETWEEN 6 AND 11 THEN 'Mañana (6-11)'
                WHEN HOUR(hora) BETWEEN 12 AND 17 THEN 'Tarde (12-17)'
                WHEN HOUR(hora) BETWEEN 18 AND 22 THEN 'Noche (18-22)'
                ELSE 'Madrugada (23-5)'
            END as franja,
            COUNT(*) as total
        FROM siniestro GROUP BY franja ORDER BY total DESC
    """)
    por_franja = cursor.fetchall()

    cursor.execute("""
        SELECT AVG(nivel_estres) as estres, AVG(nivel_ira) as ira,
               AVG(nivel_ansiedad) as ansiedad, AVG(nivel_fatiga) as fatiga
        FROM encuesta_emocional
    """)
    promedios = cursor.fetchone()

    cursor.close()
    db.close()

    # Gráfico 1: Siniestros por localidad
    fig1 = px.bar(
        x=[r['localidad'] for r in por_localidad],
        y=[r['total'] for r in por_localidad],
        title='Siniestros por Localidad',
        labels={'x': 'Localidad', 'y': 'Total'},
        color=[r['total'] for r in por_localidad],
        color_continuous_scale='Blues'
    )
    fig1.update_layout(showlegend=False)

    # Gráfico 2: Por causa oficial
    fig2 = px.pie(
        names=[r['causa_oficial'] for r in por_causa],
        values=[r['total'] for r in por_causa],
        title='Distribución por Causa Oficial',
        color_discrete_sequence=px.colors.sequential.Blues
    )

    # Gráfico 3: Por gravedad
    fig3 = px.bar(
        x=[r['gravedad'] for r in por_gravedad],
        y=[r['total'] for r in por_gravedad],
        title='Siniestros por Gravedad',
        labels={'x': 'Gravedad', 'y': 'Total'},
        color=[r['gravedad'] for r in por_gravedad],
        color_discrete_map={'Fatal': '#c0392b', 'Herido grave': '#e67e22', 'Herido': '#f1c40f'}
    )

    # Gráfico 4: Por franja horaria
    fig4 = px.bar(
        x=[r['franja'] for r in por_franja],
        y=[r['total'] for r in por_franja],
        title='Siniestros por Franja Horaria',
        labels={'x': 'Franja', 'y': 'Total'},
        color_discrete_sequence=['#1F4E79']
    )

    # Gráfico 5: Radar estado emocional
    if promedios and promedios['estres']:
        categorias = ['Estrés', 'Ira', 'Ansiedad', 'Fatiga']
        valores = [
            round(promedios['estres'] or 0, 2),
            round(promedios['ira'] or 0, 2),
            round(promedios['ansiedad'] or 0, 2),
            round(promedios['fatiga'] or 0, 2)
        ]
        fig5 = go.Figure(go.Scatterpolar(
            r=valores + [valores[0]],
            theta=categorias + [categorias[0]],
            fill='toself',
            fillcolor='rgba(31,78,121,0.3)',
            line_color='#1F4E79',
            name='Promedio emocional'
        ))
        fig5.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0, 5])),
            title='Perfil Emocional Promedio de Conductores'
        )
    else:
        fig5 = go.Figure()
        fig5.update_layout(title='Sin datos emocionales aún')

    graficos = {
        'localidad': fig1.to_html(full_html=False),
        'causa': fig2.to_html(full_html=False),
        'gravedad': fig3.to_html(full_html=False),
        'franja': fig4.to_html(full_html=False),
        'emocional': fig5.to_html(full_html=False),
    }

    return render_template('dashboard.html', graficos=graficos, promedios=promedios)


if __name__ == '__main__':
    app.run(debug=True)
