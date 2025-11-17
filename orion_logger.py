"""
ORION Centralized Logging System
Sistema de logging centralizado para todos los proyectos del portfolio
"""
import logging
import json
from datetime import datetime
from pathlib import Path
from typing import Optional


# Directorio central de logs
LOGS_DIR = Path(__file__).parent / "logs"
LOGS_DIR.mkdir(exist_ok=True)


class OrionLogger:
    """Logger centralizado para proyectos del portfolio"""

    def __init__(self, project_name: str, log_file: Optional[str] = None):
        """
        Inicializa el logger para un proyecto específico

        Args:
            project_name: Nombre del proyecto (ej: 'chat', 'scil', 'portfolio')
            log_file: Ruta personalizada del archivo de log (opcional)
        """
        self.project_name = project_name
        self.log_file = log_file or LOGS_DIR / f"{project_name}.log"
        self.logger = self._setup_logger()

    def _setup_logger(self) -> logging.Logger:
        """Configura el logger con formato JSON estructurado"""
        logger = logging.getLogger(f"orion.{self.project_name}")
        logger.setLevel(logging.INFO)

        # Evitar duplicación de handlers
        if logger.handlers:
            return logger

        # Handler para archivo (formato JSON)
        file_handler = logging.FileHandler(self.log_file, encoding='utf-8')
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(JsonFormatter())

        # Handler para consola (formato legible)
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_formatter = logging.Formatter(
            '%(asctime)s | %(name)s | %(levelname)s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        console_handler.setFormatter(console_formatter)

        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

        return logger

    def info(self, message: str, **extra):
        """Log nivel INFO"""
        self.logger.info(message, extra=extra)

    def warning(self, message: str, **extra):
        """Log nivel WARNING"""
        self.logger.warning(message, extra=extra)

    def error(self, message: str, **extra):
        """Log nivel ERROR"""
        self.logger.error(message, extra=extra)

    def critical(self, message: str, **extra):
        """Log nivel CRITICAL"""
        self.logger.critical(message, extra=extra)

    def debug(self, message: str, **extra):
        """Log nivel DEBUG"""
        self.logger.debug(message, extra=extra)

    def log_request(self, method: str, endpoint: str, status_code: int, **extra):
        """Log específico para requests HTTP"""
        self.info(
            f"{method} {endpoint} - {status_code}",
            method=method,
            endpoint=endpoint,
            status_code=status_code,
            **extra
        )

    def log_startup(self, host: str, port: int, **extra):
        """Log de inicio de aplicación"""
        self.info(
            f"Aplicación iniciada en {host}:{port}",
            event="startup",
            host=host,
            port=port,
            **extra
        )

    def log_shutdown(self, **extra):
        """Log de cierre de aplicación"""
        self.info(
            "Aplicación detenida",
            event="shutdown",
            **extra
        )

    def log_error_exception(self, exception: Exception, context: str = "", **extra):
        """Log de excepciones con contexto"""
        self.error(
            f"Excepción en {context}: {type(exception).__name__}: {str(exception)}",
            exception_type=type(exception).__name__,
            exception_message=str(exception),
            context=context,
            **extra
        )


class JsonFormatter(logging.Formatter):
    """Formatter que genera logs en formato JSON estructurado"""

    def format(self, record: logging.LogRecord) -> str:
        log_data = {
            "timestamp": datetime.utcnow().isoformat() + 'Z',
            "level": record.levelname,
            "project": record.name,
            "message": record.getMessage(),
        }

        # Agregar información extra si existe
        if hasattr(record, 'extra') and record.extra:
            log_data.update(record.extra)

        # Agregar información de excepción si existe
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_data, ensure_ascii=False)


def get_logger(project_name: str) -> OrionLogger:
    """
    Factory function para obtener un logger

    Args:
        project_name: Nombre del proyecto

    Returns:
        OrionLogger configurado
    """
    return OrionLogger(project_name)


def read_logs(project_name: str, limit: int = 100) -> list:
    """
    Lee los logs de un proyecto

    Args:
        project_name: Nombre del proyecto
        limit: Número máximo de líneas a leer (más recientes)

    Returns:
        Lista de diccionarios con los logs parseados
    """
    log_file = LOGS_DIR / f"{project_name}.log"

    if not log_file.exists():
        return []

    logs = []
    try:
        with open(log_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            # Obtener las últimas N líneas
            for line in lines[-limit:]:
                try:
                    logs.append(json.loads(line.strip()))
                except json.JSONDecodeError:
                    # Si no es JSON válido, crear entrada básica
                    logs.append({
                        "timestamp": datetime.utcnow().isoformat() + 'Z',
                        "level": "INFO",
                        "message": line.strip()
                    })
    except Exception as e:
        return [{
            "timestamp": datetime.utcnow().isoformat() + 'Z',
            "level": "ERROR",
            "message": f"Error leyendo logs: {str(e)}"
        }]

    return logs


def get_all_logs_summary() -> dict:
    """
    Obtiene un resumen de todos los logs disponibles

    Returns:
        Diccionario con información de cada proyecto
    """
    summary = {}

    for log_file in LOGS_DIR.glob("*.log"):
        project_name = log_file.stem

        try:
            # Contar líneas y obtener última entrada
            with open(log_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                total_lines = len(lines)

                last_entry = None
                if lines:
                    try:
                        last_entry = json.loads(lines[-1].strip())
                    except json.JSONDecodeError:
                        last_entry = {"message": lines[-1].strip()}

                summary[project_name] = {
                    "total_entries": total_lines,
                    "last_entry": last_entry,
                    "log_file": str(log_file)
                }
        except Exception as e:
            summary[project_name] = {
                "error": str(e)
            }

    return summary


if __name__ == "__main__":
    # Ejemplo de uso
    logger = get_logger("test")
    logger.log_startup("0.0.0.0", 5000)
    logger.info("Procesando solicitud", user="admin", action="upload")
    logger.log_request("POST", "/api/data", 200, response_time=0.25)
    logger.warning("Memoria alta", memory_usage=85.5)

    print("\n=== Logs del proyecto 'test' ===")
    for log in read_logs("test"):
        print(log)
