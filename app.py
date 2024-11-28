import os
from flask import Flask, render_template
from extensions import db  # Importa db desde extensions.py


# -------------------------------
# Inicialización de la aplicación Flask
# -------------------------------

app = Flask(__name__)

# Configuración de la clave secreta
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "eduai_companion_secret_key")

# -------------------------------
# Configuración de la base de datos
# -------------------------------

# Asegurarse de que la carpeta 'instance' exista para almacenar la base de datos SQLite
instance_path = os.path.join(os.getcwd(), 'instance')
os.makedirs(instance_path, exist_ok=True)

# Configuración de SQLite con ruta absoluta
db_path = os.path.join(instance_path, 'eduai.db')
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{db_path}"
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}

# Inicializar la extensión de SQLAlchemy
db.init_app(app)

# -------------------------------
# Registro de Blueprints
# -------------------------------

from auth import auth_bp
from questionnaire import questionnaire_bp
from chatbot import chatbot_bp

# Registrar cada módulo como un blueprint
app.register_blueprint(auth_bp)
app.register_blueprint(questionnaire_bp)
app.register_blueprint(chatbot_bp)

# -------------------------------
# Crear tablas en la base de datos
# -------------------------------

# Crear las tablas de la base de datos automáticamente si no existen
with app.app_context():
    import models  # Importa modelos después de inicializar db
    db.create_all()

# -------------------------------
# Rutas principales
# -------------------------------

@app.route('/')
def index():
    """Página principal."""
    return render_template('index.html')


@app.route('/questionnaire')
def questionnaire():
    """Ruta para el cuestionario."""
    return render_template('questionnaire.html')


@app.route('/dashboard')
def dashboard():
    """Ruta para el dashboard."""
    return render_template('dashboard.html')

# -------------------------------
# Punto de entrada para desarrollo local
# -------------------------------

if __name__ == '__main__':
    # Ejecuta la aplicación en modo local
    app.run(host='0.0.0.0', port=8000)