"""
ORION Database Manager
Gestión simplificada de base de datos SQLite
"""
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional
from contextlib import contextmanager

from config import DB_PATH


class Database:
    """Gestor de base de datos ORION"""

    def __init__(self, db_path: Path = DB_PATH):
        self.db_path = db_path
        self._init_database()

    @contextmanager
    def get_connection(self):
        """Context manager para conexiones"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def _init_database(self):
        """Inicializar tablas"""
        with self.get_connection() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS proyectos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nombre TEXT UNIQUE NOT NULL,
                    descripcion TEXT,
                    ruta TEXT NOT NULL,
                    puerto INTEGER,
                    estado TEXT DEFAULT 'detenido',
                    tipo TEXT,
                    tecnologias TEXT,
                    dependencies TEXT,
                    pid INTEGER,
                    ultima_actividad TIMESTAMP,
                    creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    actualizado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            conn.execute("""
                CREATE TABLE IF NOT EXISTS actividad (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    proyecto_id INTEGER NOT NULL,
                    tipo_evento TEXT NOT NULL,
                    descripcion TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (proyecto_id) REFERENCES proyectos(id) ON DELETE CASCADE
                )
            """)

    # ==================== PROYECTOS ====================

    def add_project(self, nombre: str, ruta: str, **kwargs) -> int:
        """Agregar proyecto"""
        with self.get_connection() as conn:
            cursor = conn.execute("""
                INSERT INTO proyectos
                (nombre, ruta, descripcion, puerto, tipo, tecnologias, dependencies, estado)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                nombre,
                ruta,
                kwargs.get('descripcion', ''),
                kwargs.get('puerto'),
                kwargs.get('tipo', ''),
                kwargs.get('tecnologias', ''),
                kwargs.get('dependencies', ''),
                kwargs.get('estado', 'detenido')
            ))
            return cursor.lastrowid

    def get_project(self, nombre: str) -> Optional[Dict]:
        """Obtener proyecto por nombre"""
        with self.get_connection() as conn:
            cursor = conn.execute("SELECT * FROM proyectos WHERE nombre = ?", (nombre,))
            row = cursor.fetchone()
            return dict(row) if row else None

    def list_projects(self, estado: Optional[str] = None) -> List[Dict]:
        """Listar proyectos"""
        with self.get_connection() as conn:
            if estado:
                cursor = conn.execute(
                    "SELECT * FROM proyectos WHERE estado = ? ORDER BY nombre",
                    (estado,)
                )
            else:
                cursor = conn.execute("SELECT * FROM proyectos ORDER BY nombre")
            return [dict(row) for row in cursor.fetchall()]

    def update_project(self, nombre: str, **kwargs):
        """Actualizar proyecto"""
        fields = []
        values = []

        for key, value in kwargs.items():
            if key in ['estado', 'puerto', 'pid', 'descripcion', 'tipo', 'tecnologias', 'dependencies']:
                fields.append(f"{key} = ?")
                values.append(value)

        if not fields:
            return

        fields.append("actualizado_en = CURRENT_TIMESTAMP")
        values.append(nombre)

        query = f"UPDATE proyectos SET {', '.join(fields)} WHERE nombre = ?"

        with self.get_connection() as conn:
            conn.execute(query, values)

    def delete_project(self, nombre: str):
        """Eliminar proyecto"""
        with self.get_connection() as conn:
            conn.execute("DELETE FROM proyectos WHERE nombre = ?", (nombre,))

    # ==================== ACTIVIDAD ====================

    def log_activity(self, nombre_proyecto: str, tipo_evento: str, descripcion: str):
        """Registrar actividad"""
        with self.get_connection() as conn:
            conn.execute("""
                INSERT INTO actividad (proyecto_id, tipo_evento, descripcion)
                SELECT id, ?, ? FROM proyectos WHERE nombre = ?
            """, (tipo_evento, descripcion, nombre_proyecto))

    def get_activity(self, nombre_proyecto: str, limit: int = 50) -> List[Dict]:
        """Obtener actividad de un proyecto"""
        with self.get_connection() as conn:
            cursor = conn.execute("""
                SELECT a.* FROM actividad a
                JOIN proyectos p ON a.proyecto_id = p.id
                WHERE p.nombre = ?
                ORDER BY a.timestamp DESC
                LIMIT ?
            """, (nombre_proyecto, limit))
            return [dict(row) for row in cursor.fetchall()]

    # ==================== UTILIDADES ====================

    def sync_projects(self, projects_info: List[Dict]):
        """Sincronizar proyectos descubiertos con la BD"""
        for project in projects_info:
            existing = self.get_project(project['nombre'])

            if not existing:
                # Agregar nuevo proyecto
                try:
                    self.add_project(
                        nombre=project['nombre'],
                        ruta=project['ruta'],
                        puerto=project.get('puerto'),
                        tipo=project.get('tipo', ''),
                        tecnologias=project.get('tecnologias', ''),
                        dependencies=','.join(project.get('dependencies', []))
                    )
                except sqlite3.IntegrityError:
                    pass
            else:
                # Actualizar info
                self.update_project(
                    nombre=project['nombre'],
                    puerto=project.get('puerto'),
                    tipo=project.get('tipo', ''),
                    tecnologias=project.get('tecnologias', ''),
                    dependencies=','.join(project.get('dependencies', []))
                )

    def get_stats(self) -> Dict:
        """Obtener estadísticas"""
        with self.get_connection() as conn:
            cursor = conn.execute("""
                SELECT
                    COUNT(*) as total,
                    SUM(CASE WHEN estado = 'activo' THEN 1 ELSE 0 END) as activos,
                    SUM(CASE WHEN estado = 'detenido' THEN 1 ELSE 0 END) as detenidos,
                    SUM(CASE WHEN estado = 'error' THEN 1 ELSE 0 END) as errores
                FROM proyectos
            """)
            row = cursor.fetchone()
            return dict(row) if row else {}


# Instancia global
db = Database()
