"""
ORION - Sistema de Gestión de Proyectos
Versión 3.0 - Modular & Minimalista
"""
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
import uvicorn

# Configuración
from config import APP_HOST, APP_PORT, APP_TITLE, APP_VERSION, APP_DESCRIPTION

# Core
from core.database import db
from core.logger import logger, get_logs_summary
from core.project_manager import project_manager

# Routers
from routers import projects, api, services

# ==================== APLICACIÓN ====================

app = FastAPI(
    title=APP_TITLE,
    version=APP_VERSION,
    description=APP_DESCRIPTION
)

# Archivos estáticos y templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Incluir routers
app.include_router(projects.router)
app.include_router(api.router)
app.include_router(services.router)


# ==================== STARTUP ====================

@app.on_event("startup")
async def startup_event():
    """Inicialización del sistema"""
    logger.info(f"Iniciando {APP_TITLE} v{APP_VERSION}")

    try:
        # Descubrir y sincronizar proyectos
        discovered = project_manager.discover_projects()
        db.sync_projects(discovered)

        logger.info(f"Sincronizados {len(discovered)} proyectos del portfolio")
    except Exception as e:
        logger.error(f"Error en startup: {str(e)}")


# ==================== DASHBOARD ====================

@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    """Dashboard principal de ORION - Lista de proyectos"""
    try:
        # Obtener todos los proyectos
        proyectos = db.list_projects()

        # Enriquecer con estado real
        for proyecto in proyectos:
            status = project_manager.get_project_status(
                proyecto['nombre'],
                proyecto.get('puerto')
            )
            proyecto.update(status)

        return templates.TemplateResponse("index.html", {
            "request": request,
            "proyectos": proyectos
        })
    except Exception as e:
        logger.error(f"Error en dashboard: {str(e)}")
        return templates.TemplateResponse("index.html", {
            "request": request,
            "proyectos": [],
            "error": str(e)
        })


# ==================== HEALTH CHECK ====================

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": APP_TITLE,
        "version": APP_VERSION
    }


# ==================== MAIN ====================

if __name__ == "__main__":
    logger.info(f"Arrancando {APP_TITLE} en {APP_HOST}:{APP_PORT}")
    uvicorn.run(app, host=APP_HOST, port=APP_PORT)
