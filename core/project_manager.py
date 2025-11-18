"""
ORION Project Manager
Gestión completa de proyectos: descubrimiento, control, dependencias
"""
import subprocess
import signal
import psutil
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import json

from config import PORTFOLIO_DIR


class ProjectManager:
    """Gestor centralizado de proyectos del portfolio"""

    def __init__(self):
        self.portfolio_dir = PORTFOLIO_DIR
        self.running_processes: Dict[str, int] = {}  # {project_name: pid}

    # ==================== DESCUBRIMIENTO ====================

    def discover_projects(self) -> List[Dict]:
        """
        Auto-descubrir proyectos en el directorio portfolio

        Returns:
            Lista de proyectos encontrados con metadata
        """
        projects = []

        if not self.portfolio_dir.exists():
            return projects

        for project_path in self.portfolio_dir.iterdir():
            if not project_path.is_dir() or project_path.name.startswith('.'):
                continue

            project_info = self._analyze_project(project_path)
            if project_info:
                projects.append(project_info)

        return sorted(projects, key=lambda x: x['nombre'])

    def _analyze_project(self, path: Path) -> Optional[Dict]:
        """
        Analizar un proyecto y extraer información

        Args:
            path: Ruta al proyecto

        Returns:
            Diccionario con información del proyecto
        """
        # Buscar archivo principal (app.py, main.py, etc.)
        main_files = ['app.py', 'main.py', 'run.py', 'server.py']
        main_file = None
        for file in main_files:
            if (path / file).exists():
                main_file = file
                break

        if not main_file:
            return None

        # Detectar tipo de proyecto
        project_type = self._detect_project_type(path)

        # Leer dependencias
        dependencies = self.read_requirements(path)

        # Detectar puerto (leer del código)
        port = self._detect_port(path / main_file)

        return {
            'nombre': path.name,
            'ruta': str(path),
            'main_file': main_file,
            'tipo': project_type,
            'puerto': port,
            'dependencies': dependencies,
            'tecnologias': ', '.join(dependencies[:5]) if dependencies else ''
        }

    def _detect_project_type(self, path: Path) -> str:
        """Detectar tipo de proyecto (Flask, FastAPI, etc.)"""
        requirements = self.read_requirements(path)

        if any('fastapi' in dep.lower() for dep in requirements):
            return 'FastAPI'
        elif any('flask' in dep.lower() for dep in requirements):
            return 'Flask'
        elif any('django' in dep.lower() for dep in requirements):
            return 'Django'
        else:
            return 'Python'

    def _detect_port(self, main_file: Path) -> Optional[int]:
        """Detectar puerto leyendo el archivo principal"""
        try:
            content = main_file.read_text()

            # Buscar patrones comunes
            import re
            patterns = [
                r'port[=\s]+(\d+)',
                r'PORT[=\s]+(\d+)',
                r'\.run\([^)]*port[=\s]+(\d+)',
                r'uvicorn\.run\([^)]*port[=\s]+(\d+)'
            ]

            for pattern in patterns:
                match = re.search(pattern, content, re.IGNORECASE)
                if match:
                    return int(match.group(1))

            return None
        except Exception:
            return None

    # ==================== DEPENDENCIAS ====================

    def read_requirements(self, path: Path) -> List[str]:
        """
        Leer requirements.txt de un proyecto

        Args:
            path: Ruta al proyecto

        Returns:
            Lista de dependencias
        """
        req_file = path / 'requirements.txt'

        if not req_file.exists():
            return []

        try:
            content = req_file.read_text()
            dependencies = []

            for line in content.split('\n'):
                line = line.strip()

                # Ignorar comentarios y líneas vacías
                if not line or line.startswith('#'):
                    continue

                # Extraer nombre del paquete (sin versión)
                if '==' in line:
                    package = line.split('==')[0].strip()
                elif '>=' in line:
                    package = line.split('>=')[0].strip()
                elif '<=' in line:
                    package = line.split('<=')[0].strip()
                else:
                    package = line.strip()

                dependencies.append(package)

            return dependencies
        except Exception:
            return []

    def get_requirements_info(self, project_name: str) -> Dict:
        """
        Obtener información detallada de requirements.txt

        Args:
            project_name: Nombre del proyecto

        Returns:
            Información de dependencias
        """
        project_path = self.portfolio_dir / project_name
        req_file = project_path / 'requirements.txt'

        if not req_file.exists():
            return {
                'exists': False,
                'dependencies': [],
                'count': 0
            }

        try:
            content = req_file.read_text()
            lines = [l.strip() for l in content.split('\n') if l.strip() and not l.startswith('#')]

            return {
                'exists': True,
                'dependencies': lines,
                'count': len(lines),
                'raw_content': content
            }
        except Exception as e:
            return {
                'exists': True,
                'error': str(e),
                'dependencies': [],
                'count': 0
            }

    # ==================== CONTROL DE PROCESOS ====================

    def start_project(self, project_name: str, port: Optional[int] = None) -> Dict:
        """
        Iniciar un proyecto

        Args:
            project_name: Nombre del proyecto
            port: Puerto (opcional, se detecta automáticamente)

        Returns:
            Resultado de la operación
        """
        project_path = self.portfolio_dir / project_name

        if not project_path.exists():
            return {'success': False, 'error': 'Proyecto no encontrado'}

        # Verificar si ya está corriendo
        if self.is_project_running(project_name):
            return {'success': False, 'error': 'Proyecto ya está en ejecución'}

        # Buscar archivo principal
        main_files = ['app.py', 'main.py', 'run.py']
        main_file = None
        for file in main_files:
            if (project_path / file).exists():
                main_file = file
                break

        if not main_file:
            return {'success': False, 'error': 'No se encontró archivo principal'}

        try:
            # Iniciar proceso
            process = subprocess.Popen(
                ['python3', main_file],
                cwd=project_path,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                start_new_session=True
            )

            self.running_processes[project_name] = process.pid

            return {
                'success': True,
                'pid': process.pid,
                'project': project_name,
                'message': f'Proyecto iniciado en PID {process.pid}'
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def stop_project(self, project_name: str) -> Dict:
        """
        Detener un proyecto

        Args:
            project_name: Nombre del proyecto

        Returns:
            Resultado de la operación
        """
        pid = self.running_processes.get(project_name)

        if not pid:
            # Intentar encontrar por puerto
            pid = self._find_pid_by_project(project_name)

        if not pid:
            return {'success': False, 'error': 'Proyecto no está corriendo'}

        try:
            # Terminar proceso
            process = psutil.Process(pid)
            process.terminate()
            process.wait(timeout=5)

            # Remover del tracking
            if project_name in self.running_processes:
                del self.running_processes[project_name]

            return {
                'success': True,
                'project': project_name,
                'message': f'Proyecto detenido (PID {pid})'
            }
        except psutil.TimeoutExpired:
            # Forzar cierre
            try:
                process.kill()
                return {
                    'success': True,
                    'project': project_name,
                    'message': 'Proyecto forzado a detener'
                }
            except Exception as e:
                return {'success': False, 'error': str(e)}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def restart_project(self, project_name: str) -> Dict:
        """Reiniciar un proyecto"""
        stop_result = self.stop_project(project_name)
        if stop_result['success']:
            import time
            time.sleep(2)  # Esperar a que libere recursos

        return self.start_project(project_name)

    # ==================== ESTADO ====================

    def is_project_running(self, project_name: str) -> bool:
        """Verificar si un proyecto está corriendo"""
        pid = self.running_processes.get(project_name)

        if pid and psutil.pid_exists(pid):
            return True

        # Intentar por puerto
        pid = self._find_pid_by_project(project_name)
        return pid is not None

    def get_project_status(self, project_name: str, port: Optional[int] = None) -> Dict:
        """
        Obtener estado completo de un proyecto

        Args:
            project_name: Nombre del proyecto
            port: Puerto del proyecto

        Returns:
            Información de estado
        """
        is_running = self.is_project_running(project_name)
        pid = self.running_processes.get(project_name) or self._find_pid_by_project(project_name)

        status = {
            'project': project_name,
            'is_running': is_running,
            'pid': pid,
            'port': port,
            'port_active': False
        }

        # Verificar puerto si se proporciona
        if port:
            status['port_active'] = self._is_port_listening(port)

        # Info del proceso si está corriendo
        if pid and psutil.pid_exists(pid):
            try:
                process = psutil.Process(pid)
                status.update({
                    'cpu_percent': process.cpu_percent(interval=0.1),
                    'memory_mb': round(process.memory_info().rss / (1024 * 1024), 2),
                    'uptime_seconds': int(process.create_time())
                })
            except Exception:
                pass

        return status

    def _find_pid_by_project(self, project_name: str) -> Optional[int]:
        """Encontrar PID de un proyecto buscando en procesos"""
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                cmdline = proc.info.get('cmdline', [])
                if cmdline and project_name in ' '.join(cmdline):
                    return proc.info['pid']
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        return None

    def _is_port_listening(self, port: int) -> bool:
        """Verificar si un puerto está en escucha"""
        for conn in psutil.net_connections(kind='inet'):
            if conn.status == 'LISTEN' and conn.laddr.port == port:
                return True
        return False

    # ==================== UTILIDADES ====================

    def get_all_project_status(self) -> List[Dict]:
        """Obtener estado de todos los proyectos"""
        projects = self.discover_projects()
        status_list = []

        for project in projects:
            status = self.get_project_status(
                project['nombre'],
                project.get('puerto')
            )
            status.update({
                'path': project['ruta'],
                'tipo': project['tipo'],
                'dependencies_count': len(project.get('dependencies', []))
            })
            status_list.append(status)

        return status_list


# Instancia global
project_manager = ProjectManager()
