"""
Ejemplo de cómo integrar ORION Logger en tus proyectos existentes
Copia este código en tus proyectos para habilitar logging centralizado
"""

# ==================== EJEMPLO PARA FLASK ====================

"""
# 1. Agregar al inicio de tu app.py
import sys
sys.path.insert(0, '/home/gabo/ORION')  # Agregar ORION al path
from orion_logger import get_logger

logger = get_logger("nombre_de_tu_proyecto")  # chat, scil, sipac, etc.

# 2. Logging al iniciar la aplicación
if __name__ == "__main__":
    logger.log_startup("0.0.0.0", 5000)  # Tu host y puerto
    logger.info("Iniciando aplicación...")

    try:
        app.run(host="0.0.0.0", port=5000, debug=False)
    except Exception as e:
        logger.log_error_exception(e, "inicio de aplicación")

# 3. Logging en rutas
@app.route("/api/data", methods=["POST"])
def procesar_datos():
    try:
        logger.info("Procesando datos", user=session.get('usuario'))
        # ... tu código ...
        logger.log_request("POST", "/api/data", 200, procesados=len(datos))
        return jsonify({"success": True})
    except Exception as e:
        logger.log_error_exception(e, "procesamiento de datos")
        return jsonify({"error": str(e)}), 500

# 4. Logging de eventos importantes
@app.route("/upload", methods=["POST"])
def subir_archivo():
    archivo = request.files.get("archivo")
    logger.info(
        f"Archivo subido: {archivo.filename}",
        filename=archivo.filename,
        size=len(archivo.read()),
        user=session.get('usuario')
    )
    # ... tu código ...
"""

# ==================== EJEMPLO PARA FASTAPI ====================

"""
# 1. Agregar al inicio de tu main.py
import sys
sys.path.insert(0, '/home/gabo/ORION')
from orion_logger import get_logger

logger = get_logger("nombre_de_tu_proyecto")

# 2. Middleware para logging automático
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    duration = time.time() - start_time

    logger.log_request(
        request.method,
        request.url.path,
        response.status_code,
        duration=round(duration, 3)
    )
    return response

# 3. Evento de inicio
@app.on_event("startup")
async def startup_event():
    logger.log_startup("0.0.0.0", 8080)
    logger.info("Aplicación FastAPI iniciada")

# 4. Evento de cierre
@app.on_event("shutdown")
async def shutdown_event():
    logger.log_shutdown()

# 5. Logging en endpoints
@app.post("/cfdi/analyze")
async def analyze_cfdi(file: UploadFile):
    try:
        logger.info(f"Analizando CFDI: {file.filename}", filename=file.filename)
        # ... tu código ...
        logger.info("CFDI analizado exitosamente", uuid=result.uuid)
        return result
    except Exception as e:
        logger.log_error_exception(e, "análisis de CFDI")
        raise HTTPException(status_code=500, detail=str(e))
"""

# ==================== EJEMPLO DE USO AVANZADO ====================

"""
# Logging con contexto adicional
logger.info(
    "Usuario autenticado",
    user_id=123,
    username="admin",
    ip=request.remote_addr,
    user_agent=request.headers.get('User-Agent')
)

# Logging de métricas
logger.info(
    "Procesamiento completado",
    total_registros=1000,
    exitosos=980,
    fallidos=20,
    tiempo_segundos=45.2,
    memoria_mb=256
)

# Logging de operaciones de base de datos
logger.info(
    "Consulta SQL ejecutada",
    query="SELECT * FROM usuarios WHERE activo = 1",
    rows_returned=150,
    execution_time_ms=23.5
)

# Warning para situaciones que requieren atención
logger.warning(
    "Espacio en disco bajo",
    disk_usage_percent=85,
    available_gb=5.2,
    threshold_gb=10
)

# Error con contexto completo
try:
    # código que puede fallar
    resultado = funcion_peligrosa()
except ValueError as e:
    logger.log_error_exception(
        e,
        "validación de datos",
        data=datos_entrada,
        expected_format="YYYY-MM-DD"
    )
"""

# ==================== LEER LOGS DESDE TU CÓDIGO ====================

"""
from orion_logger import read_logs, get_all_logs_summary

# Leer últimos 50 logs de tu proyecto
logs = read_logs("mi_proyecto", limit=50)

for log in logs:
    print(f"{log['timestamp']} [{log['level']}] {log['message']}")

# Obtener resumen de todos los logs
summary = get_all_logs_summary()

for proyecto, info in summary.items():
    print(f"{proyecto}: {info['total_entries']} entradas")
    if info['last_entry']:
        print(f"  Última: {info['last_entry']['message']}")
"""

# ==================== INTEGRACIÓN CON ORION DB ====================

"""
import sys
sys.path.insert(0, '/home/gabo/ORION')
from orion_db import OrionDB

db = OrionDB()

# Actualizar estado del proyecto cuando inicia
@app.before_first_request
def update_project_status():
    db.actualizar_estado_proyecto("mi_proyecto", "activo")

# Registrar actividad importante
@app.route("/deploy")
def deploy():
    db.registrar_actividad(
        "mi_proyecto",
        "deployment",
        "Nueva versión desplegada",
        datos_extra='{"version": "2.1.0"}'
    )
    return "Deploy exitoso"

# Actualizar cuando la app se detiene
import atexit

@atexit.register
def shutdown():
    db.actualizar_estado_proyecto("mi_proyecto", "detenido")
    logger.log_shutdown()
"""

if __name__ == "__main__":
    print("Este es un archivo de ejemplo.")
    print("Copia el código relevante a tus proyectos para integrar ORION.")
    print("\nPasos:")
    print("1. Agregar import del logger al inicio de tu app.py")
    print("2. Crear logger: logger = get_logger('nombre_proyecto')")
    print("3. Agregar logs en puntos clave de tu aplicación")
    print("4. Ver logs en: http://localhost:4090/proyecto/nombre_proyecto/logs")
