"""
ORION Configuration
Configuración centralizada del sistema
"""
from pathlib import Path

# Directorios base
BASE_DIR = Path(__file__).parent
LOGS_DIR = BASE_DIR / "logs"
DB_PATH = BASE_DIR / "orion.db"
PORTFOLIO_DIR = BASE_DIR / "portfolio" / "projects"

# Configuración de la aplicación
APP_HOST = "0.0.0.0"
APP_PORT = 4090
APP_TITLE = "ORION"
APP_VERSION = "3.0.0"
APP_DESCRIPTION = "Sistema de Gestión de Proyectos - Modular & Minimalista"

# Estados de proyectos
PROJECT_STATES = {
    "activo": "Proyecto en ejecución",
    "detenido": "Proyecto detenido",
    "error": "Proyecto con errores",
    "mantenimiento": "En mantenimiento"
}

# Rango de puertos para proyectos
PORT_RANGE_START = 4000
PORT_RANGE_END = 6000

# Logging
LOG_FORMAT = "json"
LOG_LEVEL = "INFO"

# Crear directorios necesarios
LOGS_DIR.mkdir(exist_ok=True)
PORTFOLIO_DIR.mkdir(parents=True, exist_ok=True)
