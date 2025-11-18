# 🌟 ORION v3.0

<div align="center">

**Sistema Centralizado de Gestión de Proyectos**

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104.1-green.svg)](https://fastapi.tiangolo.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Una plataforma moderna y minimalista para gestionar, monitorear y controlar múltiples proyectos de software desde un único dashboard.

[Características](#-características) •
[Instalación](#-instalación) •
[Uso](#-uso-rápido) •
[API](#-api-reference) •
[Documentación](#-documentación)

</div>

---

## ✨ Características

### 🎯 Funcionalidades Principales

- **🚀 Auto-Discovery**: Detecta automáticamente proyectos Flask/FastAPI en tu portfolio
- **⚡ Control de Procesos**: Inicia, detiene y reinicia proyectos con un click desde la interfaz
- **📊 Monitoreo en Tiempo Real**: Seguimiento de CPU, memoria, PID y puertos de cada proyecto
- **📝 Sistema de Logs**: Logging JSON centralizado con visualizador integrado y filtros
- **🔍 Gestión de Dependencias**: Lectura y visualización de archivos `requirements.txt`
- **🌳 Integración Git**: Visualiza commits, branches, status y cambios de repositorios
- **🎨 Dashboard Moderno**: Interfaz limpia, responsiva y minimalista con estadísticas en tiempo real
- **🔌 REST API Completa**: API JSON para integración programática con tus herramientas

### 🎨 Interfaz de Usuario

- **Dashboard Interactivo**: Vista general con tarjetas de proyectos y estadísticas
- **Controles Inline**: Botones de inicio/parada/reinicio directamente en cada tarjeta de proyecto
- **Visualizador de Logs**: Sistema completo de logs con filtros por nivel (INFO/WARNING/ERROR)
- **Timeline de Commits**: Historial visual de commits de Git con información detallada
- **Badges Informativos**: Muestra puertos, PIDs, uso de CPU y memoria en tiempo real
- **Diseño Responsivo**: Optimizado tanto para desktop como para dispositivos móviles

---

## 🚀 Instalación

### Requisitos Previos

- Python 3.8 o superior
- pip (gestor de paquetes de Python)
- Git (opcional, para tracking de repositorios)

### Instalación Paso a Paso

```bash
# 1. Clonar el repositorio
git clone <repository-url>
cd ORION

# 2. Crear entorno virtual (recomendado)
python -m venv venv

# Activar en Linux/Mac:
source venv/bin/activate

# Activar en Windows:
venv\Scripts\activate

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Iniciar ORION
python app.py
```

¡Listo! Accede a **http://localhost:4090** para ver el dashboard.

---

## 🎯 Uso Rápido

### Iniciar el Servidor

```bash
# Método 1: Directamente con Python
python app.py

# Método 2: Con Uvicorn (desarrollo con auto-reload)
uvicorn app:app --host 0.0.0.0 --port 4090 --reload

# Método 3: Producción con múltiples workers
uvicorn app:app --host 0.0.0.0 --port 4090 --workers 4
```

### Configurar Tus Proyectos

1. **Coloca tus proyectos** en la carpeta `portfolio/projects/`:
   ```
   ORION/
   └── portfolio/
       └── projects/
           ├── mi-app-flask/
           │   ├── app.py
           │   └── requirements.txt
           ├── mi-api-fastapi/
           │   ├── main.py
           │   └── requirements.txt
           └── otro-proyecto/
   ```

2. **Sincroniza** desde el dashboard:
   - Haz click en el botón "Sincronizar" en la interfaz web
   - O usa el endpoint API: `POST /proyectos/sync`
   - ORION detectará automáticamente los proyectos y sus dependencias

3. **Gestiona tus proyectos**:
   - ▶️ **Iniciar**: Click en el botón de play
   - ⏹️ **Detener**: Click en el botón de stop
   - 🔄 **Reiniciar**: Click en el botón de restart
   - ℹ️ **Detalles**: Click en el icono de información

### Comandos Útiles

```bash
# Ver logs en tiempo real (requiere jq)
tail -f logs/orion.log | jq .

# Consultar base de datos
sqlite3 orion.db "SELECT nombre, estado, puerto, pid FROM proyectos;"

# Verificar puertos en uso
lsof -i :4090

# Sincronizar proyectos vía API
curl -X POST http://localhost:4090/proyectos/sync
```

---

## 🏗️ Arquitectura

### Estructura del Proyecto

```
ORION/
├── app.py                      # ⚡ Aplicación FastAPI principal
├── config.py                   # ⚙️ Configuración centralizada
├── requirements.txt            # 📦 Dependencias del proyecto
├── README.md                   # 📖 Este archivo
│
├── core/                       # 🎯 Funcionalidad core
│   ├── database.py            # 💾 Gestor de base de datos SQLite
│   ├── logger.py              # 📝 Sistema de logging JSON
│   └── project_manager.py     # 🔧 Gestión y control de proyectos
│
├── services/                   # 🛠️ Servicios auxiliares
│   ├── system_monitor.py      # 📊 Monitoreo de CPU, RAM, puertos
│   └── git_service.py         # 🌳 Integración con Git
│
├── routers/                    # 🛤️ Rutas modulares
│   ├── projects.py            # Gestión de proyectos (HTML + API)
│   └── api.py                 # Endpoints REST API
│
├── templates/                  # 🎨 Templates Jinja2
│   ├── base.html              # Template base
│   ├── index.html             # 🏠 Dashboard principal
│   ├── proyecto_detalle.html  # 📄 Detalle de proyecto
│   ├── proyecto_logs.html     # 📋 Logs de proyecto específico
│   ├── all_logs.html          # 📚 Visualizador de todos los logs
│   └── commits.html           # 🌳 Historial de commits Git
│
├── static/                     # 🎨 Archivos estáticos
│   └── css/
│       └── style.css          # Estilos CSS del dashboard
│
├── logs/                       # 📝 Directorio de logs JSON
│   ├── orion.log              # Log principal de ORION
│   └── [proyecto].log         # Logs por proyecto individual
│
├── portfolio/                  # 📁 Proyectos gestionados
│   └── projects/              # Coloca aquí tus proyectos
│       ├── proyecto1/
│       ├── proyecto2/
│       └── proyecto3/
│
└── orion.db                   # 💾 Base de datos SQLite
```

### Módulos Principales

#### **config.py** - Configuración Centralizada
- Directorios del sistema (LOGS_DIR, DB_PATH, PORTFOLIO_DIR)
- Configuración de aplicación (HOST, PORT, VERSION)
- Estados de proyectos
- Rangos de puertos permitidos

#### **core/database.py** - Gestor de Base de Datos
Funciones principales:
- `add_project()` - Agregar nuevo proyecto
- `get_project(nombre)` - Obtener proyecto por nombre
- `list_projects()` - Listar todos los proyectos
- `update_project(nombre, **kwargs)` - Actualizar campos
- `sync_projects(projects)` - Sincronizar con filesystem
- `log_activity()` - Registrar eventos de proyecto

#### **core/logger.py** - Sistema de Logging
- Logging en formato JSON estructurado
- `get_logger(project_name)` - Obtener logger para proyecto
- `read_logs(project_name, limit)` - Leer logs de proyecto
- `get_logs_summary()` - Resumen de todos los logs

#### **core/project_manager.py** - Gestor de Proyectos
**Discovery:**
- `discover_projects()` - Auto-detectar proyectos en portfolio
- `read_requirements(path)` - Parsear requirements.txt

**Control:**
- `start_project(nombre)` - Iniciar proyecto como subprocess
- `stop_project(nombre)` - Detener proyecto por PID
- `restart_project(nombre)` - Reiniciar proyecto

**Monitoreo:**
- `get_project_status(nombre, puerto)` - Estado en tiempo real
- `is_project_running(nombre)` - Verificar si está ejecutándose

---

## 📚 API Reference

### Endpoints Web (HTML)

#### Dashboard y Vistas

```http
GET /
Descripción: Dashboard principal con lista de proyectos y estadísticas
Respuesta: Página HTML

GET /proyecto/{nombre}/detalle
Descripción: Vista detallada del proyecto con logs, Git y métricas
Respuesta: Página HTML

GET /proyecto/{nombre}/logs
Descripción: Logs completos del proyecto
Respuesta: Página HTML

GET /logs/all
Descripción: Visualizador de todos los logs del sistema con filtros
Respuesta: Página HTML

GET /commits
Descripción: Historial de commits de Git del repositorio ORION
Respuesta: Página HTML
```

#### Control de Proyectos

```http
POST /proyecto/{nombre}/start
Descripción: Iniciar proyecto
Respuesta: {"success": true, "pid": 12345}

POST /proyecto/{nombre}/stop
Descripción: Detener proyecto
Respuesta: {"success": true}

POST /proyecto/{nombre}/restart
Descripción: Reiniciar proyecto
Respuesta: {"success": true, "pid": 12345}

POST /proyectos/sync
Descripción: Sincronizar proyectos desde el filesystem
Respuesta: {"success": true, "projects_synced": 5, "projects": [...]}
```

### API REST (JSON)

```http
GET /api/status
Descripción: Estado general del sistema
Respuesta:
{
  "status": "ok",
  "projects_total": 5,
  "projects_active": 2
}

GET /api/proyectos
Descripción: Lista completa de proyectos con estado
Respuesta:
[
  {
    "nombre": "chat",
    "puerto": 5000,
    "estado": "activo",
    "is_running": true,
    "pid": 12345,
    "cpu_percent": 2.5,
    "memory_mb": 145.3,
    "ruta": "/path/to/chat"
  }
]

GET /api/proyecto/{nombre}
Descripción: Información detallada del proyecto
Respuesta:
{
  "nombre": "chat",
  "ruta": "/path/to/chat",
  "puerto": 5000,
  "estado": "activo",
  "pid": 12345,
  "dependencies": ["flask==2.3.0", "socketio==5.9.0"],
  "tipo": "flask",
  ...
}

GET /api/proyecto/{nombre}/logs?limit=100
Descripción: Logs del proyecto en formato JSON
Parámetros: limit (opcional, default 50)
Respuesta:
[
  {
    "timestamp": "2024-01-15T10:30:00Z",
    "level": "INFO",
    "project": "orion.chat",
    "message": "Server started on port 5000"
  }
]

GET /api/proyecto/{nombre}/status
Descripción: Estado en tiempo real del proyecto
Respuesta:
{
  "is_running": true,
  "pid": 12345,
  "cpu_percent": 2.5,
  "memory_mb": 145.3,
  "port": 5000
}

GET /health
Descripción: Health check del servicio
Respuesta:
{
  "status": "healthy",
  "service": "ORION",
  "version": "3.0.0"
}
```

### Ejemplos de Uso

#### cURL

```bash
# Obtener lista de proyectos
curl http://localhost:4090/api/proyectos | jq .

# Iniciar un proyecto
curl -X POST http://localhost:4090/proyecto/chat/start

# Ver estado en tiempo real
curl http://localhost:4090/api/proyecto/chat/status | jq .

# Obtener logs recientes
curl "http://localhost:4090/api/proyecto/chat/logs?limit=50" | jq .

# Sincronizar proyectos
curl -X POST http://localhost:4090/proyectos/sync | jq .
```

#### Python

```python
import requests

BASE_URL = "http://localhost:4090"

# Listar proyectos
response = requests.get(f"{BASE_URL}/api/proyectos")
projects = response.json()
for p in projects:
    print(f"{p['nombre']}: {'✓ Activo' if p['is_running'] else '✗ Detenido'}")

# Iniciar proyecto
response = requests.post(f"{BASE_URL}/proyecto/chat/start")
result = response.json()
if result['success']:
    print(f"Proyecto iniciado con PID: {result['pid']}")

# Monitorear recursos
response = requests.get(f"{BASE_URL}/api/proyecto/chat/status")
status = response.json()
print(f"CPU: {status['cpu_percent']}%")
print(f"RAM: {status['memory_mb']} MB")
```

---

## 🔧 Troubleshooting

### Problemas Comunes

#### ❌ Error: "no such column: pid"

La base de datos no tiene las columnas necesarias.

**Solución:**
```bash
python -c "
import sqlite3
conn = sqlite3.connect('orion.db')
conn.execute('ALTER TABLE proyectos ADD COLUMN pid INTEGER')
conn.execute('ALTER TABLE proyectos ADD COLUMN dependencies TEXT')
conn.commit()
print('✓ Columnas agregadas exitosamente')
"
```

#### ❌ Puerto 4090 ya en uso

**Solución 1 - Cambiar puerto:**
Edita `config.py`:
```python
APP_PORT = 4091  # Usar puerto diferente
```

**Solución 2 - Liberar puerto:**
```bash
# Encontrar proceso usando el puerto
lsof -i :4090

# Terminar proceso
kill -9 <PID>
```

#### ❌ Proyecto no arranca

**Checklist de diagnóstico:**
1. ✅ Verificar que el puerto del proyecto esté disponible
2. ✅ Revisar logs en `logs/[proyecto].log`
3. ✅ Verificar que existe `app.py` o `main.py` en el proyecto
4. ✅ Comprobar que las dependencias estén instaladas

**Ver logs del proyecto:**
```bash
tail -f logs/mi-proyecto.log | jq .
```

#### ❌ Logs no aparecen

**Solución:**
```bash
# Verificar que existe el directorio
ls -la logs/

# Crear si no existe
mkdir -p logs
chmod 755 logs

# Verificar permisos
ls -la logs/
```

#### ❌ Base de datos corrupta

**Solución:**
```bash
# 1. Hacer respaldo
cp orion.db orion.db.backup

# 2. Eliminar y reinicializar
rm orion.db
python -c "from core.database import db; print('✓ DB inicializada')"

# 3. Sincronizar proyectos
curl -X POST http://localhost:4090/proyectos/sync
```

---

## 🛠️ Configuración

### Variables de Configuración (config.py)

```python
# Aplicación
APP_HOST = "0.0.0.0"          # Host del servidor
APP_PORT = 4090                # Puerto del servidor
APP_TITLE = "ORION"           # Título de la aplicación
APP_VERSION = "3.0.0"         # Versión

# Directorios
LOGS_DIR = "logs"             # Directorio de logs
DB_PATH = "orion.db"          # Ruta de la base de datos
PORTFOLIO_DIR = "portfolio/projects"  # Proyectos

# Logging
LOG_LEVEL = "INFO"            # Nivel de log (DEBUG, INFO, WARNING, ERROR)

# Estados de proyecto
PROJECT_STATES = ["activo", "detenido", "error", "mantenimiento"]
```

---

## 📝 Licencia

Este proyecto está bajo la Licencia MIT - ver el archivo LICENSE para más detalles.

---

## 🙏 Agradecimientos

- **FastAPI** - Framework web moderno y de alto rendimiento
- **Uvicorn** - Servidor ASGI ultrarrápido
- **SQLite** - Base de datos embebida confiable
- **Psutil** - Librería para monitoreo de procesos y sistema
- **Jinja2** - Motor de templates potente y flexible

---

<div align="center">

**⭐ Si te gusta ORION, dale una estrella ⭐**

Desarrollado con ❤️ y Python

[Reportar Bug](https://github.com/yourusername/orion/issues) •
[Solicitar Feature](https://github.com/yourusername/orion/issues) •
[Contribuir](CONTRIBUTING.md)

</div>
