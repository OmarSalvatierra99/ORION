"""
ORION Logger
Sistema de logging simplificado con formato JSON
"""
import logging
import json
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict

from config import LOGS_DIR


class Logger:
    """Logger simplificado con JSON"""

    def __init__(self, project_name: str):
        self.project_name = project_name
        self.log_file = LOGS_DIR / f"{project_name}.log"
        self.logger = self._setup()

    def _setup(self) -> logging.Logger:
        """Configurar logger"""
        logger = logging.getLogger(f"orion.{self.project_name}")
        logger.setLevel(logging.INFO)

        if logger.handlers:
            return logger

        # Handler archivo (JSON)
        file_handler = logging.FileHandler(self.log_file, encoding='utf-8')
        file_handler.setFormatter(JsonFormatter())
        logger.addHandler(file_handler)

        # Handler consola (simple)
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(
            logging.Formatter('%(levelname)s | %(name)s | %(message)s')
        )
        logger.addHandler(console_handler)

        return logger

    def info(self, message: str, **extra):
        """Log INFO"""
        self.logger.info(message, extra=extra)

    def warning(self, message: str, **extra):
        """Log WARNING"""
        self.logger.warning(message, extra=extra)

    def error(self, message: str, **extra):
        """Log ERROR"""
        self.logger.error(message, extra=extra)

    def critical(self, message: str, **extra):
        """Log CRITICAL"""
        self.logger.critical(message, extra=extra)


class JsonFormatter(logging.Formatter):
    """Formatter JSON"""

    def format(self, record: logging.LogRecord) -> str:
        log_data = {
            "timestamp": datetime.utcnow().isoformat() + 'Z',
            "level": record.levelname,
            "project": record.name,
            "message": record.getMessage()
        }

        if hasattr(record, 'extra') and record.extra:
            log_data.update(record.extra)

        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_data, ensure_ascii=False)


# ==================== UTILIDADES ====================

def get_logger(project_name: str) -> Logger:
    """Factory para obtener logger"""
    return Logger(project_name)


def read_logs(project_name: Optional[str] = None, limit: int = 100) -> List[Dict]:
    """
    Leer logs de un proyecto o todos los proyectos

    Args:
        project_name: Nombre del proyecto (None para todos)
        limit: Límite de logs a retornar

    Returns:
        Lista de logs ordenados por timestamp (más recientes primero)
    """
    if project_name:
        # Leer logs de un proyecto específico
        log_file = LOGS_DIR / f"{project_name}.log"

        if not log_file.exists():
            return []

        logs = []
        try:
            with open(log_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                for line in lines[-limit:]:
                    try:
                        logs.append(json.loads(line.strip()))
                    except json.JSONDecodeError:
                        logs.append({
                            "timestamp": datetime.utcnow().isoformat() + 'Z',
                            "level": "INFO",
                            "message": line.strip()
                        })
        except Exception:
            return []

        return logs
    else:
        # Leer todos los logs de todos los proyectos
        all_logs = []

        try:
            for log_file in sorted(LOGS_DIR.glob("*.log"), reverse=True):
                try:
                    with open(log_file, 'r', encoding='utf-8') as f:
                        # Leer últimas 100 líneas de cada archivo
                        lines = f.readlines()[-100:]
                        for line in lines:
                            try:
                                log_entry = json.loads(line.strip())
                                all_logs.append(log_entry)
                            except json.JSONDecodeError:
                                all_logs.append({
                                    "timestamp": datetime.utcnow().isoformat() + 'Z',
                                    "level": "INFO",
                                    "message": line.strip()
                                })
                except Exception:
                    continue
        except Exception:
            return []

        # Ordenar por timestamp (más recientes primero)
        all_logs.sort(
            key=lambda x: x.get('timestamp', ''),
            reverse=True
        )
        return all_logs[:limit]


def get_logs_summary() -> Dict[str, Dict]:
    """Resumen de todos los logs"""
    summary = {}

    for log_file in LOGS_DIR.glob("*.log"):
        project_name = log_file.stem

        try:
            with open(log_file, 'r') as f:
                lines = f.readlines()
                last_entry = None

                if lines:
                    try:
                        last_entry = json.loads(lines[-1].strip())
                    except json.JSONDecodeError:
                        last_entry = {"message": lines[-1].strip()}

                summary[project_name] = {
                    "total_entries": len(lines),
                    "last_entry": last_entry
                }
        except Exception:
            continue

    return summary


# Logger global de ORION
logger = get_logger("orion")
