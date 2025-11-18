"""
Router de Proyectos
Gestión de proyectos del portfolio
"""
from fastapi import APIRouter, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse

from core.database import db
from core.logger import read_logs, logger
from core.project_manager import project_manager

templates = Jinja2Templates(directory="templates")
router = APIRouter()


# ==================== VISTAS HTML ====================

@router.get("/proyectos", response_class=HTMLResponse)
async def list_projects(request: Request):
    """Vista de gestión de proyectos"""
    try:
        # Obtener proyectos de la BD
        proyectos = db.list_projects()

        # Enriquecer con estado real
        for proyecto in proyectos:
            status = project_manager.get_project_status(
                proyecto['nombre'],
                proyecto.get('puerto')
            )
            proyecto.update(status)

        return templates.TemplateResponse("proyectos.html", {
            "request": request,
            "proyectos": proyectos
        })
    except Exception as e:
        logger.error(f"Error listando proyectos: {str(e)}")
        return templates.TemplateResponse("proyectos.html", {
            "request": request,
            "proyectos": [],
            "error": str(e)
        })


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

        # Requirements info
        req_info = project_manager.get_requirements_info(nombre)

        # Actividad reciente
        actividad = db.get_activity(nombre, limit=20)

        # Logs recientes
        logs = read_logs(nombre, limit=10)

        return templates.TemplateResponse("proyecto_detalle.html", {
            "request": request,
            "proyecto": proyecto,
            "requirements": req_info,
            "actividad": actividad,
            "logs": logs
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
