"""
Router de Sistema
Monitoreo de recursos, puertos y procesos
"""
from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse

from core.database import db
from core.logger import logger
from services.system_monitor import (
    SystemMonitor, PortMonitor, ProcessMonitor, get_system_summary
)

templates = Jinja2Templates(directory="templates")
router = APIRouter()


# ==================== VISTAS HTML ====================

@router.get("/sistema", response_class=HTMLResponse)
async def system_dashboard(request: Request):
    """Dashboard de monitoreo del sistema"""
    try:
        system_info = get_system_summary()
        top_cpu = ProcessMonitor.get_top_processes(limit=10, sort_by='cpu')
        top_memory = ProcessMonitor.get_top_processes(limit=10, sort_by='memory')

        return templates.TemplateResponse("sistema.html", {
            "request": request,
            "system": system_info,
            "top_cpu": top_cpu,
            "top_memory": top_memory
        })
    except Exception as e:
        logger.error(f"Error en sistema dashboard: {str(e)}")
        return HTMLResponse(f"Error: {str(e)}", status_code=500)


@router.get("/puertos", response_class=HTMLResponse)
async def ports_dashboard(request: Request):
    """Dashboard de monitoreo de puertos"""
    try:
        proyectos = db.list_projects()
        listening_ports = PortMonitor.get_listening_ports()
        project_ports = PortMonitor.get_project_ports(proyectos)

        return templates.TemplateResponse("puertos.html", {
            "request": request,
            "listening_ports": listening_ports,
            "project_ports": project_ports,
            "total_listening": len(listening_ports)
        })
    except Exception as e:
        logger.error(f"Error en puertos dashboard: {str(e)}")
        return HTMLResponse(f"Error: {str(e)}", status_code=500)


# ==================== API ====================

@router.get("/api/sistema")
async def get_system_info():
    """API: Información del sistema"""
    try:
        return {
            "success": True,
            "data": get_system_summary()
        }
    except Exception as e:
        logger.error(f"Error obteniendo info del sistema: {str(e)}")
        return {"success": False, "error": str(e)}


@router.get("/api/puertos")
async def get_ports_info():
    """API: Información de puertos"""
    try:
        proyectos = db.list_projects()
        return {
            "success": True,
            "listening_ports": PortMonitor.get_listening_ports(),
            "project_ports": PortMonitor.get_project_ports(proyectos)
        }
    except Exception as e:
        logger.error(f"Error obteniendo info de puertos: {str(e)}")
        return {"success": False, "error": str(e)}


@router.get("/api/procesos")
async def get_processes_info(limit: int = 20, sort_by: str = 'cpu'):
    """API: Información de procesos"""
    try:
        processes = ProcessMonitor.get_top_processes(limit=limit, sort_by=sort_by)

        return {
            "success": True,
            "count": len(processes),
            "sort_by": sort_by,
            "processes": processes
        }
    except Exception as e:
        logger.error(f"Error obteniendo info de procesos: {str(e)}")
        return {"success": False, "error": str(e)}
