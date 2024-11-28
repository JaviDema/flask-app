# EduAI Companion 🤖
## 📚 Descripción
EduAI Companion es un chatbot educativo inteligente que personaliza la experiencia de aprendizaje según el perfil del usuario. Utiliza modelos avanzados de IA y análisis adaptativo para ofrecer una experiencia educativa única.

-> [Aplicación implementada](https://x0dev-chatEduAI.replit.app)

## 🚀 Características Principales
### Sistema de Autenticación JWT
- Login seguro basado en tokens
- Gestión de sesiones sin estado
- Tokens de acceso seguros
### Perfiles de Usuario Adaptativos
- **Estructurado:** Aprendizaje metódico y analítico
- **Explorador:** Aprendizaje flexible y descubrimiento
- **Intensivo:** Aprendizaje directo y práctico
### Sistema de Métricas
- Dimensión Temporal (20 puntos)
- Dimensión Metodológica (30 puntos)
- Dimensión Motivacional (25 puntos)
- Dimensión de Contenido (25 puntos)

## 🛠️ Tecnologías
- Python/Flask
- SQLAlchemy
- JWT
- MistralAI
- Bootstrap/JavaScript
- NLTK para procesamiento de lenguaje natural
- TF-IDF y Análisis de Coseno para búsqueda de similitud

## ⚙️ Instalación y Configuración Rápida

```bash
# 1. Clonar repositorio
git clone https://github.com/x0dev-ai/EduAI-Companion.git
cd EduAI-Companion

# 2. Crear y activar entorno virtual (opcional pero recomendado)
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate

# 3. Instalar todas las dependencias desde requirements.txt
pip install -r requirements.txt

# 4. Configurar variables de entorno
export FLASK_SECRET_KEY="tu_clave_secreta"  # En Windows: set FLASK_SECRET_KEY=tu_clave_secreta
export MISTRAL_API_KEY="tu_api_key_de_mistral"  # En Windows: set MISTRAL_API_KEY=tu_api_key_de_mistral

# 5. Iniciar la aplicación
python main.py
```

La aplicación estará disponible en `http://localhost:5000`

## 📦 Requisitos del Sistema
- Python >= 3.11
- Todas las dependencias listadas en `requirements.txt`:
  ```
  flask>=3.0.3
  flask-sqlalchemy>=3.1.1
  PyJWT>=2.8.0
  mistralai==0.4.2
  nltk>=3.9.1
  scikit-learn>=1.5.2
  Werkzeug>=3.0.1
  python-dateutil>=2.8.2
  numpy>=1.24.0
  ```

## 🗂️ Estructura del Proyecto
```
EduAI-Companion/
├── instance/           # Base de datos SQLite
├── static/            # Archivos estáticos (CSS, JS)
├── templates/         # Plantillas HTML
├── nltk_data/         # Datos de NLTK
├── app.py            # Configuración principal de Flask
├── main.py           # Punto de entrada de la aplicación
├── auth.py           # Sistema de autenticación
├── chatbot.py        # Lógica del chatbot
├── models.py         # Modelos de la base de datos
├── requirements.txt  # Lista de dependencias
└── questionnaire.py  # Lógica del cuestionario
```

## 🚀 Uso
1. **Registro/Login:**
   - Accede a la página principal
   - Obtén un token de acceso
   - Inicia sesión con el token

2. **Configuración del Perfil:**
   - Completa el cuestionario inicial
   - El sistema determinará tu perfil de aprendizaje

3. **Interacción con el Chatbot:**
   - Accede al dashboard
   - Realiza preguntas al chatbot
   - Recibe respuestas personalizadas según tu perfil

4. **Seguimiento del Progreso:**
   - Revisa tus métricas de aprendizaje
   - Consulta el historial de interacciones
   - Analiza tu evolución

## 🔧 Solución de Problemas Comunes
1. **Error de base de datos:**
   - Verifica que existe el directorio `instance`
   - Asegúrate de tener permisos de escritura

2. **Error con NLTK:**
   - Los datos de NLTK se descargan automáticamente
   - Si hay problemas, ejecuta manualmente:
     ```python
     import nltk
     nltk.download('punkt')
     nltk.download('stopwords')
     nltk.download('averaged_perceptron_tagger')
     ```

3. **Error con MistralAI:**
   - Verifica que tienes la versión correcta (0.4.2)
   - Asegúrate de tener una API key válida

4. **Problemas con las dependencias:**
   - Si encuentras conflictos, intenta instalar las dependencias una por una:
     ```bash
     pip install -r requirements.txt --no-deps
     pip install <paquete_específico>
     ```

## 👥 Contribución
1. Fork del proyecto
2. Crear rama: `git checkout -b feature/nueva-caracteristica`
3. Commit: `git commit -m 'Añadir característica'`
4. Push: `git push origin feature/nueva-caracteristica`
5. Pull Request

## 📄 Licencia
Este proyecto está bajo la Licencia MIT.

## 🤝 Soporte
Para soporte, contactar: [x0dev.ai@gmail.com](mailto:x0dev.ai@gmail.com)

## 🌟 Roadmap
- Integración con más APIs educativas
- Soporte multilenguaje
- Análisis predictivo avanzado
- Sistema de gamificación
---

Desarrollado con ❤️ por X0DEV
