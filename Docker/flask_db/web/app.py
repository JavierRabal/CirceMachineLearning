from flask import Flask, render_template, request, redirect, url_for
import psycopg2
import os
import time

app = Flask(__name__)

# --- Configuración de la Base de Datos ---
# Las variables de entorno son inyectadas por Docker Compose
DB_HOST = os.environ.get('DB_HOST', 'localhost')
DB_NAME = os.environ.get('DB_NAME', 'flask_db')
DB_USER = os.environ.get('DB_USER', 'flask_user')
DB_PASS = os.environ.get('DB_PASS', 'supersecret')

def get_db_connection():
    """Intenta conectar a la base de datos con reintentos para esperar a Postgres."""
    conn = None
    max_retries = 10
    retry_delay = 5  # segundos

    for i in range(max_retries):
        try:
            conn = psycopg2.connect(
                host=DB_HOST,
                database=DB_NAME,
                user=DB_USER,
                password=DB_PASS
            )
            print(f"Conexión a la BBDD exitosa después de {i} intentos.")
            return conn
        except psycopg2.OperationalError as e:
            print(f"Error de conexión a la BBDD. Reintentando en {retry_delay}s... (Intento {i+1}/{max_retries})")
            if i < max_retries - 1:
                time.sleep(retry_delay)
            else:
                raise # Lanza el error si se agotan los reintentos

def init_db():
    """Inicializa la tabla de mensajes si no existe."""
    conn = None
    try:
        # Usamos un delay inicial para dar tiempo a que el servicio 'db' se levante
        time.sleep(10) 
        conn = get_db_connection()
        cur = conn.cursor()
        # Crear la tabla 'messages'
        cur.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id SERIAL PRIMARY KEY,
                content TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        conn.commit()
        cur.close()
        print("Tabla 'messages' verificada/creada correctamente.")
    except Exception as e:
        # En caso de error, lo imprime y la app puede continuar si el error es leve
        print(f"Error al inicializar la BBDD: {e}")
    finally:
        if conn:
            conn.close()

# Inicializa la base de datos al arrancar la aplicación
init_db()

@app.route('/', methods=('GET', 'POST'))
def index():
    """Maneja el formulario de ingreso de datos."""
    if request.method == 'POST':
        message_content = request.form.get('content')
        if message_content:
            conn = None
            try:
                conn = get_db_connection()
                cur = conn.cursor()
                # Insertar el nuevo mensaje de forma segura
                cur.execute('INSERT INTO messages (content) VALUES (%s)', (message_content,))
                conn.commit()
                cur.close()
            except Exception as e:
                print(f"Error al insertar el mensaje: {e}")
            finally:
                if conn:
                    conn.close()
            # Redirigir para evitar que el formulario se envíe de nuevo al recargar
            return redirect(url_for('index')) 

    # Renderiza la plantilla con el formulario
    return render_template('index.html')

@app.route('/results')
def results():
    """Muestra todos los mensajes guardados en la BBDD."""
    conn = None
    messages = []
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        # Selecciona todos los mensajes, ordenados por fecha descendente
        cur.execute('SELECT id, content, created_at FROM messages ORDER BY created_at DESC;')
        messages = cur.fetchall()
        cur.close()
    except Exception as e:
        print(f"Error al obtener los mensajes de la BBDD: {e}")
        # En un entorno real, puedes registrar el error o mostrar un aviso al usuario
    finally:
        if conn:
            conn.close()

    # Renderiza la plantilla con los mensajes
    return render_template('second.html', messages=messages)

if __name__ == '__main__':
    # Flask se ejecutará dentro de Docker en 0.0.0.0
    app.run(host='0.0.0.0', port=5000, debug=True)