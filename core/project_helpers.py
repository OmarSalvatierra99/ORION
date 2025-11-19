"""
ORION Project Helpers
Funciones auxiliares para proyectos
"""
from typing import List, Dict
from core.project_manager import project_manager


def enrich_projects_with_status(projects_list: List[Dict]) -> List[Dict]:
    """
    Enriquecer proyectos con estado en tiempo real

    Agrega información de estado (is_running, PID, CPU, memoria) a cada proyecto.

    Args:
        projects_list: Lista de proyectos de la base de datos

    Returns:
        Lista de proyectos con estado actualizado

    Example:
        >>> proyectos = db.list_projects()
        >>> enrich_projects_with_status(proyectos)
    """
    for proyecto in projects_list:
        status = project_manager.get_project_status(
            proyecto['nombre'],
            proyecto.get('puerto')
        )
        proyecto.update(status)
    return projects_list
