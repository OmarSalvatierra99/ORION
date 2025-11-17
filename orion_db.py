"""
ORION Database Manager
Gestión centralizada de proyectos de software en la nube
"""
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional, Any
from contextlib import contextmanager


DB_PATH = Path(__file__).parent / "orion.db"


class OrionDB:
    """Gestor de base de datos para ORION"""

    def __init__(self, db_path: Path = DB_PATH):
        self.db_path = db_path
        self.init_database()

    @contextmanager
    def get_connection(self):
        """Context manager para conexiones a la base de datos"""
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

    def init_database(self):
        """Inicializa las tablas de la base de datos"""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            # Tabla de proyectos
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS proyectos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nombre TEXT UNIQUE NOT NULL,
                    descripcion TEXT,
                    ruta TEXT NOT NULL,
                    puerto INTEGER,
                    estado TEXT DEFAULT 'detenido',
                    ultima_actividad TIMESTAMP,
                    tipo TEXT,
                    tecnologias TEXT,
                    creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    actualizado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Tabla de actividad de proyectos
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS actividad_proyectos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    proyecto_id INTEGER NOT NULL,
                    tipo_evento TEXT NOT NULL,
                    descripcion TEXT,
                    datos_extra TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (proyecto_id) REFERENCES proyectos(id) ON DELETE CASCADE
                )
            """)

    # ==================== PROYECTOS ====================

    def agregar_proyecto(self, nombre: str, ruta: str, **kwargs) -> int:
        """
        Agrega un nuevo proyecto

        Args:
            nombre: Nombre del proyecto
            ruta: Ruta al directorio del proyecto
            **kwargs: Campos opcionales (descripcion, puerto, tipo, tecnologias)

        Returns:
            ID del proyecto creado
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO proyectos (nombre, ruta, descripcion, puerto, tipo, tecnologias)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                nombre,
                ruta,
                kwargs.get('descripcion', ''),
                kwargs.get('puerto'),
                kwargs.get('tipo', ''),
                kwargs.get('tecnologias', '')
            ))
            return cursor.lastrowid

    def actualizar_estado_proyecto(self, nombre: str, estado: str, log_actividad: bool = True):
        """
        Actualiza el estado de un proyecto

        Args:
            nombre: Nombre del proyecto
            estado: Nuevo estado (activo, detenido, error, mantenimiento)
            log_actividad: Si se debe registrar en la tabla de actividad
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE proyectos
                SET estado = ?,
                    ultima_actividad = CURRENT_TIMESTAMP,
                    actualizado_en = CURRENT_TIMESTAMP
                WHERE nombre = ?
            """, (estado, nombre))

            if log_actividad:
                cursor.execute("""
                    INSERT INTO actividad_proyectos (proyecto_id, tipo_evento, descripcion)
                    SELECT id, 'cambio_estado', ?
                    FROM proyectos WHERE nombre = ?
                """, (f"Estado cambiado a: {estado}", nombre))

    def obtener_proyecto(self, nombre: str) -> Optional[Dict]:
        """Obtiene información de un proyecto por nombre"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM proyectos WHERE nombre = ?", (nombre,))
            row = cursor.fetchone()
            return dict(row) if row else None

    def listar_proyectos(self, estado: Optional[str] = None) -> List[Dict]:
        """
        Lista todos los proyectos

        Args:
            estado: Filtrar por estado (opcional)

        Returns:
            Lista de proyectos
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            if estado:
                cursor.execute("SELECT * FROM proyectos WHERE estado = ? ORDER BY nombre", (estado,))
            else:
                cursor.execute("SELECT * FROM proyectos ORDER BY nombre")
            return [dict(row) for row in cursor.fetchall()]

    def registrar_actividad(self, nombre_proyecto: str, tipo_evento: str, descripcion: str, datos_extra: str = ""):
        """Registra actividad de un proyecto"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO actividad_proyectos (proyecto_id, tipo_evento, descripcion, datos_extra)
                SELECT id, ?, ?, ?
                FROM proyectos WHERE nombre = ?
            """, (tipo_evento, descripcion, datos_extra, nombre_proyecto))

    def obtener_actividad_proyecto(self, nombre_proyecto: str, limit: int = 50) -> List[Dict]:
        """Obtiene el historial de actividad de un proyecto"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT a.* FROM actividad_proyectos a
                JOIN proyectos p ON a.proyecto_id = p.id
                WHERE p.nombre = ?
                ORDER BY a.timestamp DESC
                LIMIT ?
            """, (nombre_proyecto, limit))
            return [dict(row) for row in cursor.fetchall()]



def inicializar_proyectos_portfolio():
    """Función helper para inicializar proyectos del portfolio automáticamente"""
    db = OrionDB()
    proyectos_base = Path(__file__).parent / "portfolio" / "projects"

    if not proyectos_base.exists():
        return

    proyectos_info = {
        "chat": {"puerto": 5002, "tipo": "Flask", "tecnologias": "Flask, SQLAlchemy, SocketIO"},
        "cleandoc": {"puerto": 4085, "tipo": "Flask", "tecnologias": "Flask, python-docx"},
        "factulab": {"puerto": 8080, "tipo": "FastAPI", "tecnologias": "FastAPI, lxml, ReportLab"},
        "lexnum": {"puerto": 4055, "tipo": "Flask", "tecnologias": "Flask, pandas, openpyxl"},
        "procesar-xml": {"puerto": 4080, "tipo": "Flask", "tecnologias": "Flask, pandas, defusedxml"},
        "scan-actas": {"puerto": 5045, "tipo": "Flask", "tecnologias": "Flask, OpenCV, PyMuPDF"},
        "scil": {"puerto": 4050, "tipo": "Flask", "tecnologias": "Flask, pandas, SQLite"},
        "sicobo": {"puerto": 5035, "tipo": "Flask", "tecnologias": "Flask, pandas"},
        "sipac": {"puerto": 5020, "tipo": "Flask", "tecnologias": "Flask, PostgreSQL, pandas"},
    }

    for nombre, info in proyectos_info.items():
        proyecto_dir = proyectos_base / nombre
        if proyecto_dir.exists():
            try:
                db.agregar_proyecto(
                    nombre=nombre,
                    ruta=str(proyecto_dir),
                    descripcion=f"Proyecto {nombre} del portfolio",
                    **info
                )
                print(f"✓ Proyecto '{nombre}' agregado")
            except sqlite3.IntegrityError:
                # El proyecto ya existe
                pass


if __name__ == "__main__":
    # Ejemplo de uso
    db = OrionDB()

    print("=== Inicializando proyectos del portfolio ===")
    inicializar_proyectos_portfolio()

    print("\n=== Proyectos registrados ===")
    for proyecto in db.listar_proyectos():
        print(f"- {proyecto['nombre']} ({proyecto['estado']}) - Puerto {proyecto['puerto']}")

    print(f"\n✓ Total de proyectos: {len(db.listar_proyectos())}")
