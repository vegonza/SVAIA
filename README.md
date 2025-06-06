# SVAIA: Sistema de soporte para Vulnerabilidades y Amenazas basado en Inteligencia Artificial

**Trabajo universitario de la Universidad de Málaga (UMA) - Equipo TideLock**

---

## 🚀 Descripción
SVAIA es una plataforma web desarrollada como trabajo universitario para la Universidad de Málaga (UMA). Utiliza Inteligencia Artificial para analizar proyectos y ofrecer sugerencias de seguridad sobre vulnerabilidades y amenazas. Permite a los usuarios subir archivos de proyectos (Docker Compose, Dockerfiles, imágenes) y recibir recomendaciones automáticas basadas en miles de vulnerabilidades conocidas y la información más reciente de la industria.

## 🛠️ Tecnologías principales
- **Backend:** Python, Flask, Flask-Login, Flask-SQLAlchemy, Flask-CORS
- **IA:** OpenAI API (vía openrouter.ai)
- **Frontend:** HTML, CSS (Bootstrap + estilos propios), JavaScript
- **Base de datos:** SQLite (por defecto, configurable)
- **Otros:** python-dotenv, nvdlib

## ✨ Funcionalidades principales
- Autenticación de usuarios y gestión de sesiones (control de acceso seguro)
- Subida y análisis de proyectos (Docker Compose, Dockerfiles, imágenes Docker)
- Chat interactivo con IA para sugerencias de seguridad
- Panel de administración para gestión de usuarios y proyectos
- Sistema de agentes inteligentes para análisis y sugerencias personalizadas
- Sistema de logs para auditoría y trazabilidad de acciones
- Scripts de enumeración de subdominios

## 📦 Estructura del proyecto
```
├── app.py                # App principal Flask
├── run.py                # Entrada alternativa (PythonAnywhere)
├── requirements.txt      # Dependencias
├── example.env           # Variables de entorno de ejemplo
├── frontend/             # Plantillas y estáticos (JS, CSS, imágenes)
├── services/             # Blueprints: auth, chat, sql, admin
├── libs/                 # Utilidades (logging, etc.)
├── subdomains/           # Scripts de enumeración de subdominios
├── logs/                 # Archivos de log
├── instance/db.sqlite    # Base de datos SQLite por defecto
└── README                # Este archivo
```

## ⚡ Instalación y ejecución
1. **Clona el repositorio:**
   ```bash
   git clone <repo-url>
   cd <nombre-del-repo>
   ```
2. **Instala las dependencias:**
   ```bash
   pip install -r requirements.txt
   ```
3. **Configura las variables de entorno:**
   - Copia `example.env` a `.env` y completa tus claves:
     - `AI_API_KEY`: Tu clave de OpenAI
     - `APP_SECRET_KEY`: Clave secreta Flask
     - `GOOGLE_MAPS_API_KEY`: (opcional, para mapas)
     - `PYTHONANYWHERE_DB`: (opcional, URI de BD personalizada)
4. **Ejecuta la app:**
   ```bash
   python app.py
   ```
   O para despliegue (ej. PythonAnywhere):
   ```bash
   python run.py
   ```

## 🧑‍💻 ¿Cómo se usa?
1. Regístrate o inicia sesión.
2. Crea un nuevo proyecto y sube tus archivos (Docker Compose, Dockerfiles, imágenes Docker).
3. Accede al chat y recibe sugerencias de seguridad generadas por IA.
4. (Opcional) Si eres admin, gestiona usuarios y proyectos desde el panel de administración.
