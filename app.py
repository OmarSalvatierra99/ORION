from fastapi import FastAPI, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from typing import Optional
from datetime import datetime
import uvicorn

# Importar módulos de ORION
from orion_db import OrionDB, inicializar_proyectos_portfolio
from orion_logger import get_logger, read_logs, get_all_logs_summary

# Inicializar FastAPI
app = FastAPI(title="ORION", description="Sistema de Gestión de Proyectos Flask")

# Configurar archivos estáticos y templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Inicializar base de datos y logger
db = OrionDB()
logger = get_logger("orion")


# ==================== STARTUP ====================
@app.on_event("startup")
async def startup_event():
    """Inicializar ORION al arrancar"""
    logger.log_startup("0.0.0.0", 4090)
    # Inicializar proyectos automáticamente si no existen
    try:
        inicializar_proyectos_portfolio()
        logger.info("Proyectos del portfolio inicializados")
    except Exception as e:
        logger.log_error_exception(e, "inicialización de proyectos")


# ==================== RUTAS PRINCIPALES ====================
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Dashboard principal de ORION"""
    try:
        # Obtener estadísticas de proyectos
        proyectos = db.listar_proyectos()
        proyectos_activos = [p for p in proyectos if p['estado'] == 'activo']
        proyectos_error = [p for p in proyectos if p['estado'] == 'error']
        logs_summary = get_all_logs_summary()

        stats = {
            "total_proyectos": len(proyectos),
            "proyectos_activos": len(proyectos_activos),
            "proyectos_error": len(proyectos_error),
            "proyectos_con_logs": len(logs_summary)
        }

        return templates.TemplateResponse("index.html", {
            "request": request,
            "stats": stats,
            "proyectos": proyectos[:6]  # Primeros 6 proyectos para el dashboard
        })
    except Exception as e:
        logger.log_error_exception(e, "dashboard principal")
        return templates.TemplateResponse("index.html", {"request": request})


# ==================== PROYECTOS ====================
@app.get("/proyectos", response_class=HTMLResponse)
async def listar_proyectos(request: Request):
    """Vista de gestión de proyectos"""
    try:
        proyectos = db.listar_proyectos()
        return templates.TemplateResponse("proyectos.html", {
            "request": request,
            "proyectos": proyectos
        })
    except Exception as e:
        logger.log_error_exception(e, "listar proyectos")
        return templates.TemplateResponse("proyectos.html", {
            "request": request,
            "proyectos": []
        })


@app.get("/proyecto/{nombre}/logs", response_class=HTMLResponse)
async def ver_logs_proyecto(request: Request, nombre: str):
    """Ver logs de un proyecto específico"""
    try:
        proyecto = db.obtener_proyecto(nombre)
        if not proyecto:
            return HTMLResponse("Proyecto no encontrado", status_code=404)

        logs = read_logs(nombre, limit=200)

        return templates.TemplateResponse("proyecto_logs.html", {
            "request": request,
            "proyecto": proyecto,
            "logs": logs
        })
    except Exception as e:
        logger.log_error_exception(e, f"logs de {nombre}")
        return HTMLResponse(f"Error al cargar logs: {str(e)}", status_code=500)


@app.get("/proyecto/{nombre}/detalle", response_class=HTMLResponse)
async def detalle_proyecto(request: Request, nombre: str):
    """Ver detalles completos de un proyecto"""
    try:
        proyecto = db.obtener_proyecto(nombre)
        if not proyecto:
            return HTMLResponse("Proyecto no encontrado", status_code=404)

        actividad = db.obtener_actividad_proyecto(nombre, limit=50)
        logs = read_logs(nombre, limit=10)

        return templates.TemplateResponse("proyecto_detalle.html", {
            "request": request,
            "proyecto": proyecto,
            "actividad": actividad,
            "logs_recientes": logs
        })
    except Exception as e:
        logger.log_error_exception(e, f"detalle de {nombre}")
        return HTMLResponse(f"Error: {str(e)}", status_code=500)


@app.post("/api/proyecto/{nombre}/estado")
async def actualizar_estado_proyecto(nombre: str, estado: str = Form(...)):
    """Actualizar estado de un proyecto"""
    try:
        db.actualizar_estado_proyecto(nombre, estado)
        logger.info(f"Estado de {nombre} actualizado a {estado}")
        return JSONResponse({"success": True, "estado": estado})
    except Exception as e:
        logger.log_error_exception(e, f"actualizar estado de {nombre}")
        return JSONResponse({"success": False, "error": str(e)}, status_code=500)


# ==================== API ENDPOINTS ====================
@app.get("/api/status")
async def get_status():
    """Estado del sistema"""
    try:
        proyectos = db.listar_proyectos()
        logs_summary = get_all_logs_summary()

        return {
            "status": "online",
            "assistant": "ORION",
            "version": "2.0",
            "timestamp": datetime.utcnow().isoformat(),
            "proyectos": {
                "total": len(proyectos),
                "activos": len([p for p in proyectos if p['estado'] == 'activo']),
                "detenidos": len([p for p in proyectos if p['estado'] == 'detenido']),
                "error": len([p for p in proyectos if p['estado'] == 'error'])
            },
            "logs": {
                "proyectos_con_logs": len(logs_summary)
            }
        }
    except Exception as e:
        logger.log_error_exception(e, "api status")
        return {"status": "error", "error": str(e)}


@app.get("/api/proyectos")
async def api_proyectos():
    """Listar proyectos en formato JSON"""
    try:
        proyectos = db.listar_proyectos()
        return {"success": True, "proyectos": proyectos}
    except Exception as e:
        return {"success": False, "error": str(e)}


@app.get("/api/logs/{proyecto}")
async def api_logs(proyecto: str, limit: int = 100):
    """Obtener logs de un proyecto en formato JSON"""
    try:
        logs = read_logs(proyecto, limit=limit)
        return {"success": True, "proyecto": proyecto, "logs": logs}
    except Exception as e:
        return {"success": False, "error": str(e)}


if __name__ == "__main__":
    logger.info("Iniciando ORION - Sistema de Gestión de Proyectos")
    uvicorn.run(app, host="0.0.0.0", port=4090)
