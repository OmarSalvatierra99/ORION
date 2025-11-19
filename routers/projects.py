"""
Router de Proyectos
Gestión de proyectos del portfolio
"""
from pathlib import Path
import json

from fastapi import APIRouter, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse

from config import LOGS_DIR, BASE_DIR
from core.database import db
from core.logger import read_logs, logger
from core.project_manager import project_manager
from services.git_service import GitManager

templates = Jinja2Templates(directory="templates")
router = APIRouter()


# ==================== VISTAS HTML ====================


@router.get("/proyecto/{nombre}/detalle", response_class=HTMLResponse)
async def project_detail(request: Request, nombre: str):
    """Vista detallada de un proyecto"""
    try:
        proyecto = db.get_project(nombre)
        if not proyecto:
            return HTMLResponse("Proyecto no encontrado", status_code=404)

        # Estado real
        status = project_manager.get_project_status(nombre, proyecto.get('puerto'))
        proyecto.update(status)

        # Logs recientes
        logs = read_logs(nombre, limit=20)

        # Git status
        git_manager = GitManager(proyecto['ruta'])
        git_status = None
        if git_manager.is_git_repo():
            git_status = git_manager.get_git_status()

        return templates.TemplateResponse("proyecto_detalle.html", {
            "request": request,
            "proyecto": proyecto,
            "logs": logs,
            "git_status": git_status
        })
    except Exception as e:
        logger.error(f"Error en detalle de {nombre}: {str(e)}")
        return HTMLResponse(f"Error: {str(e)}", status_code=500)


@router.get("/proyecto/{nombre}/logs", response_class=HTMLResponse)
async def project_logs(request: Request, nombre: str):
    """Vista de logs de un proyecto"""
    try:
        proyecto = db.get_project(nombre)
        if not proyecto:
            return HTMLResponse("Proyecto no encontrado", status_code=404)

        logs = read_logs(nombre, limit=200)

        return templates.TemplateResponse("proyecto_logs.html", {
            "request": request,
            "proyecto": proyecto,
            "logs": logs
        })
    except Exception as e:
        logger.error(f"Error en logs de {nombre}: {str(e)}")
        return HTMLResponse(f"Error: {str(e)}", status_code=500)


@router.get("/logs/all", response_class=HTMLResponse)
async def all_logs(request: Request):
    """Vista de todos los logs del sistema"""
    try:
        # Usar función refactorizada read_logs() sin proyecto específico
        logs = read_logs(project_name=None, limit=500)

        return templates.TemplateResponse("all_logs.html", {
            "request": request,
            "logs": logs
        })
    except Exception as e:
        logger.error(f"Error en vista de todos los logs: {str(e)}")
        return HTMLResponse(f"Error: {str(e)}", status_code=500)


@router.get("/commits", response_class=HTMLResponse)
async def commits_view(request: Request):
    """Vista de historial de commits de ORION"""
    try:
        git_manager = GitManager(str(BASE_DIR))

        commits = []
        error = None

        if git_manager.is_git_repo():
            commits_data = git_manager.get_recent_commits(limit=50)
            if commits_data and not commits_data.get('error'):
                commits = commits_data.get('commits', [])
        else:
            error = "El directorio ORION no es un repositorio Git"

        return templates.TemplateResponse("commits.html", {
            "request": request,
            "commits": commits,
            "error": error
        })
    except Exception as e:
        logger.error(f"Error en vista de commits: {str(e)}")
        return templates.TemplateResponse("commits.html", {
            "request": request,
            "commits": [],
            "error": str(e)
        })


# ==================== ACCIONES ====================

@router.post("/proyecto/{nombre}/start")
async def start_project(nombre: str):
    """Iniciar un proyecto"""
    try:
        result = project_manager.start_project(nombre)

        if result['success']:
            db.update_project(nombre, estado='activo', pid=result.get('pid'))
            db.log_activity(nombre, 'inicio', f"Proyecto iniciado (PID: {result.get('pid')})")
            logger.info(f"Proyecto {nombre} iniciado", pid=result.get('pid'))

        return JSONResponse(result)
    except Exception as e:
        logger.error(f"Error iniciando {nombre}: {str(e)}")
        return JSONResponse({"success": False, "error": str(e)}, status_code=500)


@router.post("/proyecto/{nombre}/stop")
async def stop_project(nombre: str):
    """Detener un proyecto"""
    try:
        result = project_manager.stop_project(nombre)

        if result['success']:
            db.update_project(nombre, estado='detenido', pid=None)
            db.log_activity(nombre, 'detencion', "Proyecto detenido")
            logger.info(f"Proyecto {nombre} detenido")

        return JSONResponse(result)
    except Exception as e:
        logger.error(f"Error deteniendo {nombre}: {str(e)}")
        return JSONResponse({"success": False, "error": str(e)}, status_code=500)


@router.post("/proyecto/{nombre}/restart")
async def restart_project(nombre: str):
    """Reiniciar un proyecto"""
    try:
        result = project_manager.restart_project(nombre)

        if result['success']:
            db.update_project(nombre, estado='activo', pid=result.get('pid'))
            db.log_activity(nombre, 'reinicio', f"Proyecto reiniciado (PID: {result.get('pid')})")
            logger.info(f"Proyecto {nombre} reiniciado")

        return JSONResponse(result)
    except Exception as e:
        logger.error(f"Error reiniciando {nombre}: {str(e)}")
        return JSONResponse({"success": False, "error": str(e)}, status_code=500)


@router.post("/proyecto/{nombre}/estado")
async def update_project_state(nombre: str, estado: str = Form(...)):
    """Actualizar estado manual de un proyecto"""
    try:
        db.update_project(nombre, estado=estado)
        db.log_activity(nombre, 'cambio_estado', f"Estado cambiado a: {estado}")
        logger.info(f"Estado de {nombre} actualizado a {estado}")

        return JSONResponse({"success": True, "estado": estado})
    except Exception as e:
        logger.error(f"Error actualizando estado de {nombre}: {str(e)}")
        return JSONResponse({"success": False, "error": str(e)}, status_code=500)


# ==================== SINCRONIZACIÓN ====================

@router.post("/proyectos/sync")
async def sync_projects():
    """Sincronizar proyectos del filesystem con la BD"""
    try:
        # Descubrir proyectos
        discovered = project_manager.discover_projects()

        # Sincronizar con BD
        db.sync_projects(discovered)

        logger.info(f"Sincronizados {len(discovered)} proyectos")

        return JSONResponse({
            "success": True,
            "projects_synced": len(discovered),
            "projects": discovered
        })
    except Exception as e:
        logger.error(f"Error sincronizando proyectos: {str(e)}")
        return JSONResponse({"success": False, "error": str(e)}, status_code=500)
