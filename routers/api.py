"""
Router API
Endpoints REST para acceso programático
"""
from pathlib import Path

from fastapi import APIRouter
from datetime import datetime

from core.database import db
from core.logger import read_logs, get_logs_summary, logger
from core.project_manager import project_manager
from core.project_helpers import enrich_projects_with_status

router = APIRouter(prefix="/api")


@router.get("/status")
async def get_status():
    """Estado general del sistema"""
    try:
        stats = db.get_stats()
        logs_summary = get_logs_summary()

        return {
            "status": "online",
            "assistant": "ORION",
            "version": "3.0.0",
            "timestamp": datetime.utcnow().isoformat(),
            "proyectos": stats,
            "logs": {
                "proyectos_con_logs": len(logs_summary)
            }
        }
    except Exception as e:
        logger.error(f"Error en API status: {str(e)}")
        return {"status": "error", "error": str(e)}


@router.get("/proyectos")
async def list_projects():
    """Listar todos los proyectos"""
    try:
        proyectos = db.list_projects()

        # Enriquecer con estado real
        proyectos = enrich_projects_with_status(proyectos)

        return {
            "success": True,
            "count": len(proyectos),
            "proyectos": proyectos
        }
    except Exception as e:
        logger.error(f"Error listando proyectos: {str(e)}")
        return {"success": False, "error": str(e)}


@router.get("/proyecto/{nombre}")
async def get_project(nombre: str):
    """Obtener información completa de un proyecto incluyendo análisis de app.py"""
    try:
        proyecto = db.get_project(nombre)

        if not proyecto:
            return {"success": False, "error": "Proyecto no encontrado"}

        # Estado real
        status = project_manager.get_project_status(nombre, proyecto.get('puerto'))

        # Requirements
        req_info = project_manager.get_requirements_info(nombre)

        # Análisis completo del proyecto (re-analizar para obtener datos frescos)
        project_path = Path(proyecto['ruta'])
        if project_path.exists():
            analysis = project_manager.analyze_project(project_path)
        else:
            analysis = None

        return {
            "success": True,
            "proyecto": proyecto,
            "status": status,
            "requirements": req_info,
            "analysis": {
                "endpoints": analysis.get('endpoints', []) if analysis else [],
                "imports": analysis.get('imports', []) if analysis else [],
                "descripcion": analysis.get('descripcion', '') if analysis else '',
                "has_database": analysis.get('has_database', False) if analysis else False,
                "has_auth": analysis.get('has_auth', False) if analysis else False,
                "endpoints_count": len(analysis.get('endpoints', [])) if analysis else 0,
                "imports_count": len(analysis.get('imports', [])) if analysis else 0
            }
        }
    except Exception as e:
        logger.error(f"Error obteniendo {nombre}: {str(e)}")
        return {"success": False, "error": str(e)}


@router.get("/proyecto/{nombre}/logs")
async def get_project_logs(nombre: str, limit: int = 100):
    """Obtener logs de un proyecto"""
    try:
        logs = read_logs(nombre, limit=limit)

        return {
            "success": True,
            "proyecto": nombre,
            "count": len(logs),
            "logs": logs
        }
    except Exception as e:
        logger.error(f"Error obteniendo logs de {nombre}: {str(e)}")
        return {"success": False, "error": str(e)}


@router.get("/proyecto/{nombre}/requirements")
async def get_project_requirements(nombre: str):
    """Obtener requirements.txt de un proyecto"""
    try:
        req_info = project_manager.get_requirements_info(nombre)

        return {
            "success": True,
            "proyecto": nombre,
            "requirements": req_info
        }
    except Exception as e:
        logger.error(f"Error obteniendo requirements de {nombre}: {str(e)}")
        return {"success": False, "error": str(e)}


@router.get("/proyecto/{nombre}/status")
async def get_project_status(nombre: str):
    """Obtener estado en tiempo real de un proyecto"""
    try:
        proyecto = db.get_project(nombre)

        if not proyecto:
            return {"success": False, "error": "Proyecto no encontrado"}

        status = project_manager.get_project_status(nombre, proyecto.get('puerto'))

        return {
            "success": True,
            "proyecto": nombre,
            "status": status
        }
    except Exception as e:
        logger.error(f"Error obteniendo status de {nombre}: {str(e)}")
        return {"success": False, "error": str(e)}


@router.get("/proyecto/{nombre}/analysis")
async def get_project_analysis(nombre: str):
    """Obtener análisis detallado de app.py de un proyecto"""
    try:
        proyecto = db.get_project(nombre)

        if not proyecto:
            return {"success": False, "error": "Proyecto no encontrado"}

        # Analizar proyecto
        project_path = Path(proyecto['ruta'])

        if not project_path.exists():
            return {"success": False, "error": "Ruta del proyecto no existe"}

        analysis = project_manager.analyze_project(project_path)

        if not analysis:
            return {"success": False, "error": "No se pudo analizar el proyecto"}

        return {
            "success": True,
            "proyecto": nombre,
            "analysis": {
                "tipo": analysis.get('tipo', 'Unknown'),
                "main_file": analysis.get('main_file', ''),
                "puerto": analysis.get('puerto'),
                "descripcion": analysis.get('descripcion', ''),
                "endpoints": analysis.get('endpoints', []),
                "endpoints_count": len(analysis.get('endpoints', [])),
                "imports": analysis.get('imports', []),
                "imports_count": len(analysis.get('imports', [])),
                "dependencies": analysis.get('dependencies', []),
                "dependencies_count": len(analysis.get('dependencies', [])),
                "features": {
                    "has_database": analysis.get('has_database', False),
                    "has_auth": analysis.get('has_auth', False)
                }
            }
        }
    except Exception as e:
        logger.error(f"Error analizando {nombre}: {str(e)}")
        return {"success": False, "error": str(e)}


@router.get("/logs/summary")
async def get_all_logs_summary():
    """Resumen de todos los logs"""
    try:
        summary = get_logs_summary()

        return {
            "success": True,
            "count": len(summary),
            "summary": summary
        }
    except Exception as e:
        logger.error(f"Error obteniendo summary de logs: {str(e)}")
        return {"success": False, "error": str(e)}
