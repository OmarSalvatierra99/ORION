# 🌟 ORION - Guía de Usuario

## Asistente Virtual Inteligente para Gestión de Proyectos y Finanzas

ORION es tu asistente centralizado para administrar todos tus proyectos del portfolio y tus finanzas personales.

---

## 🚀 Inicio Rápido

### 1. Iniciar ORION

```bash
cd /home/gabo/ORION
source venv/bin/activate
python app.py
```

ORION estará disponible en: **http://localhost:4090**

### 2. Inicializar Proyectos (Primera vez)

```bash
python orion_db.py
```

Este comando:
- Crea la base de datos SQLite (`orion.db`)
- Registra todos los proyectos de `portfolio/projects/`
- Inicializa el sistema de logs

---

## 📊 Funcionalidades

### 1. Gestión de Proyectos

#### Ver todos los proyectos
- **URL**: http://localhost:4090/proyectos
- Visualiza todos tus proyectos con su estado, puerto y tecnologías

#### Ver logs de un proyecto
- **URL**: http://localhost:4090/proyecto/{nombre}/logs
- Ejemplo: http://localhost:4090/proyecto/scil/logs
- Filtra logs por nivel (INFO, WARNING, ERROR, CRITICAL)

#### Estados de proyectos
Los proyectos pueden estar en:
- ✅ **activo**: Proyecto corriendo
- ⏸️ **detenido**: Proyecto pausado
- ❌ **error**: Proyecto con errores
- 🔧 **mantenimiento**: En actualización

### 2. Sistema de Logging

Cada proyecto puede usar el logger centralizado de ORION:

```python
from orion_logger import get_logger

# En tu proyecto
logger = get_logger("mi_proyecto")

# Logs básicos
logger.info("Servidor iniciado")
logger.warning("Memoria al 80%")
logger.error("Error de conexión")

# Logs especializados
logger.log_startup("0.0.0.0", 5000)
logger.log_request("POST", "/api/data", 200)
logger.log_error_exception(exception, "contexto")
```

**Logs se guardan en**: `/home/gabo/ORION/logs/{proyecto}.log`

Formato JSON estructurado:
```json
{
  "timestamp": "2025-11-17T10:30:00Z",
  "level": "INFO",
  "project": "orion.scil",
  "message": "Servidor iniciado",
  "host": "0.0.0.0",
  "port": 4050
}
```

### 3. Gestión de Deudas

#### Ver todas las deudas
- **URL**: http://localhost:4090/deudas
- Dashboard con:
  - Deuda total
  - Total pagado
  - Saldo pendiente
  - Deudas vencidas

#### Agregar nueva deuda
- **URL**: http://localhost:4090/deudas/nueva
- Campos:
  - Descripción
  - Monto
  - Acreedor
  - Fecha de vencimiento
  - Categoría (financiera, personal, etc.)
  - Notas

#### Registrar pago
1. Ir a detalles de la deuda
2. Click en "Pagar"
3. Ingresar:
   - Monto del pago
   - Fecha
   - Método de pago
   - Notas

El sistema automáticamente:
- Actualiza el saldo
- Marca como "pagada" cuando saldo = 0
- Calcula deudas vencidas

---

## 🔧 Configuración de Proyectos

### Integrar logging en tus proyectos

#### Para proyectos Flask:

```python
from orion_logger import get_logger

logger = get_logger("mi_proyecto")

@app.before_request
def log_request():
    logger.log_request(
        request.method,
        request.path,
        200  # Actualizar en @app.after_request
    )

@app.route("/")
def index():
    logger.info("Página principal accedida")
    return render_template("index.html")

if __name__ == "__main__":
    logger.log_startup("0.0.0.0", 5000)
    app.run(host="0.0.0.0", port=5000)
```

#### Para proyectos FastAPI:

```python
from orion_logger import get_logger

logger = get_logger("mi_proyecto")

@app.on_event("startup")
async def startup_event():
    logger.log_startup("0.0.0.0", 8000)

@app.middleware("http")
async def log_requests(request, call_next):
    response = await call_next(request)
    logger.log_request(
        request.method,
        request.url.path,
        response.status_code
    )
    return response
```

---

## 📡 API Endpoints

### Estado del sistema
```bash
GET /api/status
```

Respuesta:
```json
{
  "status": "online",
  "assistant": "ORION",
  "timestamp": "2025-11-17T10:30:00",
  "proyectos": {
    "total": 9,
    "activos": 2
  },
  "deudas": {
    "total": 5,
    "saldo_pendiente": 15000.00
  },
  "logs": {
    "proyectos_con_logs": 3
  }
}
```

### Listar proyectos
```bash
GET /api/proyectos
```

### Listar deudas
```bash
GET /api/deudas
```

### Obtener logs de un proyecto
```bash
GET /api/logs/{proyecto}?limit=100
```

### Actualizar estado de proyecto
```bash
POST /api/proyecto/{nombre}/estado
Content-Type: application/x-www-form-urlencoded

estado=activo
```

---

## 📁 Estructura de Archivos

```
/home/gabo/ORION/
├── app.py                  # Aplicación principal FastAPI
├── orion_db.py            # Gestor de base de datos
├── orion_logger.py        # Sistema de logging centralizado
├── orion.db               # Base de datos SQLite
├── logs/                  # Logs de todos los proyectos
│   ├── orion.log
│   ├── scil.log
│   ├── chat.log
│   └── ...
├── templates/             # Plantillas HTML
│   ├── index.html
│   ├── proyectos.html
│   ├── proyecto_logs.html
│   ├── deudas.html
│   └── ...
├── static/                # Archivos estáticos
├── venv/                  # Entorno virtual
└── requirements.txt
```

---

## 💡 Casos de Uso

### 1. Monitorear un proyecto en producción

```bash
# Terminal 1: Ver logs en tiempo real
tail -f logs/scil.log | jq .

# Terminal 2: Actualizar estado
curl -X POST http://localhost:4090/api/proyecto/scil/estado \
  -d "estado=activo"
```

### 2. Control financiero mensual

1. Ir a http://localhost:4090/deudas
2. Revisar deudas vencidas
3. Registrar pagos del mes
4. Ver resumen actualizado

### 3. Debugging de errores

1. Ir a http://localhost:4090/proyecto/scil/logs
2. Filtrar por "ERROR" o "CRITICAL"
3. Analizar stack traces en formato JSON
4. Correlacionar con actividad del proyecto

---

## 🔐 Base de Datos

### Tablas

#### proyectos
- `id`, `nombre`, `descripcion`, `ruta`, `puerto`
- `estado`, `ultima_actividad`, `tipo`, `tecnologias`
- `creado_en`, `actualizado_en`

#### deudas
- `id`, `descripcion`, `monto`, `moneda`, `acreedor`
- `fecha_inicio`, `fecha_vencimiento`, `estado`
- `categoria`, `notas`, `pagado`
- `creado_en`, `actualizado_en`

#### pagos_deuda
- `id`, `deuda_id`, `monto`, `fecha_pago`
- `metodo_pago`, `notas`, `creado_en`

#### actividad_proyectos
- `id`, `proyecto_id`, `tipo_evento`, `descripcion`
- `datos_extra`, `timestamp`

### Consultas útiles

```sql
-- Ver proyectos activos
SELECT nombre, puerto, ultima_actividad
FROM proyectos
WHERE estado = 'activo';

-- Deudas próximas a vencer
SELECT descripcion, monto, fecha_vencimiento,
       (monto - pagado) as saldo
FROM deudas
WHERE estado != 'pagada'
  AND fecha_vencimiento <= date('now', '+7 days')
ORDER BY fecha_vencimiento;

-- Actividad reciente de todos los proyectos
SELECT p.nombre, a.tipo_evento, a.descripcion, a.timestamp
FROM actividad_proyectos a
JOIN proyectos p ON a.proyecto_id = p.id
ORDER BY a.timestamp DESC
LIMIT 20;
```

---

## 🎨 Personalización

### Agregar nuevos proyectos manualmente

```python
from orion_db import OrionDB

db = OrionDB()
db.agregar_proyecto(
    nombre="nuevo_proyecto",
    ruta="/ruta/al/proyecto",
    descripcion="Descripción del proyecto",
    puerto=5050,
    tipo="Flask",
    tecnologias="Flask, PostgreSQL, Redis"
)
```

### Registrar actividad personalizada

```python
db.registrar_actividad(
    nombre_proyecto="scil",
    tipo_evento="deploy",
    descripcion="Deployed versión 2.0 a producción",
    datos_extra='{"version": "2.0", "server": "vps-01"}'
)
```

---

## 🐛 Solución de Problemas

### ORION no inicia

```bash
# Verificar dependencias
source venv/bin/activate
pip install -r requirements.txt

# Verificar puerto disponible
lsof -i :4090

# Reiniciar base de datos
rm orion.db
python orion_db.py
```

### Los logs no aparecen

```bash
# Verificar directorio de logs
ls -la logs/

# Verificar permisos
chmod 755 logs/

# Probar logger manualmente
python -c "from orion_logger import get_logger; logger = get_logger('test'); logger.info('Test')"
```

### Deudas no se calculan correctamente

```bash
# Recalcular saldos
sqlite3 orion.db "
UPDATE deudas
SET estado = 'pagada'
WHERE pagado >= monto;
"
```

---

## 📚 Recursos Adicionales

- **Documentación FastAPI**: https://fastapi.tiangolo.com
- **SQLite Docs**: https://www.sqlite.org/docs.html
- **Jinja2 Templates**: https://jinja.palletsprojects.com

---

## 🤝 Soporte

Para problemas o sugerencias, revisar:
1. Logs de ORION: `logs/orion.log`
2. Estado de la base de datos: `sqlite3 orion.db`
3. CLAUDE.md para detalles técnicos

---

**ORION** - Asistente Virtual Inteligente
*Desarrollado para gestión eficiente de proyectos y finanzas personales*
