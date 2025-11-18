"""
Router de Servicios y Puertos
Vista de monitoreo de servicios activos y puertos en uso
"""
from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse

from core.database import db
from core.logger import logger
from core.project_manager import project_manager
from services.system_monitor import (
    SystemMonitor,
    PortMonitor,
    ProcessMonitor,
    get_system_summary
)

templates = Jinja2Templates(directory="templates")
router = APIRouter()


# ==================== VISTAS HTML ====================

@router.get("/servicios", response_class=HTMLResponse)
async def services_dashboard(request: Request):
    """
    Dashboard de servicios activos y puertos

    Muestra:
    - Servicios (proyectos) en ejecución
    - Puertos en uso con detalles
    - Información de sistema en tiempo real
    """
    try:
        # Obtener todos los proyectos
        proyectos = db.list_projects()

        # Enriquecer con estado real
        active_services = []
        inactive_services = []

        for proyecto in proyectos:
            status = project_manager.get_project_status(
                proyecto['nombre'],
                proyecto.get('puerto')
            )
            proyecto.update(status)

            if proyecto.get('is_running'):
                active_services.append(proyecto)
            else:
                inactive_services.append(proyecto)

        # Obtener puertos en escucha
        listening_ports = PortMonitor.get_listening_ports()

        # Información del sistema
        system_info = {
            'cpu': SystemMonitor.get_cpu_info(),
            'memory': SystemMonitor.get_memory_info(),
            'process_count': ProcessMonitor.get_process_count()
        }

        # Cruzar información de puertos con proyectos
        project_ports = PortMonitor.get_project_ports(proyectos)

        return templates.TemplateResponse("servicios.html", {
            "request": request,
            "active_services": active_services,
            "inactive_services": inactive_services,
            "listening_ports": listening_ports,
            "project_ports": project_ports,
            "system_info": system_info,
            "total_services": len(proyectos),
            "active_count": len(active_services),
            "ports_count": len(listening_ports)
        })
    except Exception as e:
        logger.error(f"Error en dashboard de servicios: {str(e)}")
        return HTMLResponse(f"Error: {str(e)}", status_code=500)


# ==================== API ENDPOINTS ====================

@router.get("/api/servicios")
async def get_services_api():
    """
    API endpoint para obtener información de servicios activos

    Returns:
        JSON con servicios activos, puertos y estado del sistema
    """
    try:
        # Obtener todos los proyectos
        proyectos = db.list_projects()

        # Enriquecer con estado real
        active_services = []
        inactive_services = []

        for proyecto in proyectos:
            status = project_manager.get_project_status(
                proyecto['nombre'],
                proyecto.get('puerto')
            )
            proyecto.update(status)

            if proyecto.get('is_running'):
                active_services.append(proyecto)
            else:
                inactive_services.append(proyecto)

        # Puertos en escucha
        listening_ports = PortMonitor.get_listening_ports()

        # Información del sistema
        system_summary = get_system_summary()

        return {
            "success": True,
            "services": {
                "total": len(proyectos),
                "active": len(active_services),
                "inactive": len(inactive_services),
                "active_list": active_services,
                "inactive_list": inactive_services
            },
            "ports": {
                "total": len(listening_ports),
                "listening": listening_ports
            },
            "system": system_summary
        }
    except Exception as e:
        logger.error(f"Error en API de servicios: {str(e)}")
        return {"success": False, "error": str(e)}


@router.get("/api/puertos")
async def get_ports_api():
    """
    API endpoint específico para información de puertos

    Returns:
        JSON con todos los puertos en escucha y sus procesos
    """
    try:
        listening_ports = PortMonitor.get_listening_ports()
        proyectos = db.list_projects()
        project_ports = PortMonitor.get_project_ports(proyectos)

        return {
            "success": True,
            "ports": {
                "total": len(listening_ports),
                "listening": listening_ports,
                "projects": project_ports
            }
        }
    except Exception as e:
        logger.error(f"Error en API de puertos: {str(e)}")
        return {"success": False, "error": str(e)}


@router.get("/api/sistema")
async def get_system_api():
    """
    API endpoint para información completa del sistema

    Returns:
        JSON con CPU, memoria, disco, red y procesos
    """
    try:
        system_summary = get_system_summary()
        top_processes = ProcessMonitor.get_top_processes(limit=10)

        return {
            "success": True,
            "system": system_summary,
            "top_processes": top_processes
        }
    except Exception as e:
        logger.error(f"Error en API de sistema: {str(e)}")
        return {"success": False, "error": str(e)}
