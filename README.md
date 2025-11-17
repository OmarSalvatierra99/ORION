# 🌟 ORION - Sistema de Gestión de Proyectos Flask

Sistema centralizado de gestión, generación y monitoreo de proyectos Flask con **control de Git** y **monitoreo de recursos**.

## 🚀 Características Principales

### 📊 Gestión de Proyectos
- Monitoreo centralizado de proyectos del portfolio
- **Generador automático de proyectos Flask** con plantillas completas
- Sistema de logs en formato JSON
- Control de estados (activo, detenido, error, mantenimiento)
- Dashboard con estadísticas en tiempo real

### 🔧 Generador de Proyectos
- **Creación automática** de proyectos Flask con estructura completa
- Plantillas HTML con Jinja2
- Integración automática con ORION Logger
- Configuración de base de datos SQLite (opcional)
- Endpoints API REST (opcional)
- Inicialización automática de Git
- Entorno virtual incluido
- **Sugerencia inteligente de puertos** disponibles

### 🔌 Monitor de Puertos
- Visualización de todos los puertos en escucha
- **Detección automática** de procesos por puerto
- Estado de puertos asignados a proyectos
- Identificación de conflictos de puertos
- PID y comando de cada proceso

### 📦 Gestión Git
- **Estado de repositorios** en tiempo real
- Commits recientes de cada proyecto
- Archivos modificados por proyecto
- Información de branches y remotos
- Integración con GitHub
- Detección de cambios sin commit

### 💻 Monitor del Sistema
- **Monitoreo en tiempo real** de CPU, memoria y disco
- Listado de procesos top por CPU y memoria
- Información de red (datos enviados/recibidos)
- Tiempo de actividad del sistema
- Estadísticas de recursos en vivo

## 📦 Instalación

### 1. Clonar y configurar entorno

```bash
git clone <repository-url>
cd ORION
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Inicializar Base de Datos

```bash
python orion_db.py
```

Esto creará:
- Base de datos SQLite (`orion.db`)
- Registrará proyectos del portfolio
- Inicializará tablas de deudas y actividad

### 3. Ejecutar ORION

```bash
python app.py
```

ORION estará disponible en: **http://localhost:4090**

## 🎯 Uso de Funcionalidades

### 🆕 Generar un Nuevo Proyecto Flask

1. Ir a **http://localhost:4090/generar**
2. Ingresar:
   - **Nombre del proyecto** (ej: `mi-api-rest`)
   - **Puerto** (ORION sugiere automáticamente puertos disponibles)
   - **Descripción** (opcional)
   - **Características**: Templates, API, Base de Datos
3. Click en **"Generar Proyecto"**
4. El proyecto se crea automáticamente en `portfolio/projects/`

**El proyecto generado incluye:**
- ✅ Aplicación Flask configurada
- ✅ Templates HTML base con diseño moderno
- ✅ Integración con ORION Logger
- ✅ Entorno virtual (venv)
- ✅ Repositorio Git inicializado
- ✅ README.md completo
- ✅ .gitignore configurado
- ✅ requirements.txt con dependencias

### 📊 Monitor de Puertos

1. Ir a **http://localhost:4090/puertos**
2. Ver:
   - Puertos asignados a tus proyectos
   - Estado (ACTIVO/INACTIVO)
   - Proceso que ocupa cada puerto
   - Todos los puertos en escucha del sistema

### 🔄 Gestión Git

1. Ir a **http://localhost:4090/git**
2. Ver para cada proyecto:
   - Branch actual
   - Último commit
   - Archivos modificados
   - Commits recientes
   - URL remota de GitHub

### 💻 Monitor del Sistema

1. Ir a **http://localhost:4090/sistema**
2. Monitorear:
   - Uso de CPU y memoria
   - Espacio en disco
   - Procesos top por CPU/memoria
   - Red y estadísticas del sistema

## 🛠️ API Endpoints

### Gestión de Proyectos

```bash
# Estado del sistema
GET /api/status

# Listar proyectos
GET /api/proyectos

# Estado de un proyecto
GET /proyecto/{nombre}/detalle

# Actualizar estado de proyecto
POST /api/proyecto/{nombre}/estado
  Body: estado=activo

# Logs de proyecto
GET /api/logs/{proyecto}?limit=100
```

### Generador de Proyectos

```bash
# Generar nuevo proyecto Flask
POST /api/generar
  Body:
    nombre=mi-proyecto
    puerto=5100
    descripcion=Mi nuevo proyecto
    with_database=true
    with_api=true
    with_templates=true
```

### Monitor de Puertos

```bash
# Obtener información de puertos
GET /api/puertos

# Respuesta:
{
  "listening_ports": [...],
  "project_ports": [...]
}
```

### Gestión Git

```bash
# Estado Git de un proyecto
GET /api/git/{proyecto}

# Respuesta:
{
  "status": {...},
  "commits": [...],
  "branches": [...]
}
```

### Monitor del Sistema

```bash
# Información del sistema
GET /api/sistema

# Respuesta:
{
  "cpu": {...},
  "memory": {...},
  "disk": [...],
  "network": {...}
}
```

## 📁 Estructura del Proyecto

```
ORION/
├── app.py                      # FastAPI app principal
├── orion_db.py                 # Gestor de base de datos
├── orion_logger.py             # Sistema de logging
├── orion_git.py                # 🆕 Gestor de Git
├── orion_system.py             # 🆕 Monitor de sistema
├── orion_generator.py          # 🆕 Generador de proyectos
├── orion.db                    # Base de datos SQLite
├── requirements.txt            # Dependencias Python
├── logs/                       # Logs JSON de proyectos
├── templates/                  # Templates HTML
│   ├── base.html              # Template base
│   ├── index.html             # Dashboard
│   ├── proyectos.html         # Lista de proyectos
│   ├── generar.html           # 🆕 Generador de proyectos
│   ├── puertos.html           # 🆕 Monitor de puertos
│   ├── git.html               # 🆕 Gestión Git
│   ├── sistema.html           # 🆕 Monitor de sistema
│   ├── proyecto_logs.html     # Visor de logs
│   └── proyecto_detalle.html  # Detalle de proyecto
├── static/                     # Archivos estáticos
│   ├── css/style.css          # Estilos
│   └── js/app.js              # JavaScript
├── portfolio/projects/         # 🆕 Proyectos generados
└── venv/                       # Entorno virtual
```

## 🔧 Configuración Avanzada

### Personalizar Plantillas de Proyectos

Edita `orion_generator.py` para modificar:
- Estructura de archivos generados
- Templates HTML base
- Configuración de Flask
- Dependencias por defecto

### Cambiar Puerto de ORION

Edita `app.py` (última línea):
```python
uvicorn.run(app, host="0.0.0.0", port=4090)  # Cambiar 4090
```

### Personalizar Ruta de Proyectos

Por defecto: `portfolio/projects/`

Edita `orion_generator.py`:
```python
def __init__(self, portfolio_path: str = "tu/ruta/personalizada"):
```

## 🐛 Solución de Problemas

### Error "psutil not found"

```bash
pip install psutil==5.9.6
```

### Proyectos no aparecen en Git

Verifica que los proyectos tengan repositorio Git inicializado:
```bash
cd portfolio/projects/tu-proyecto
git status
```

### Puerto ya en uso

1. Ir a **Monitor de Puertos** para identificar el proceso
2. Cambiar puerto del proyecto o detener el proceso conflictivo

## 📚 Recursos

- [FastAPI Docs](https://fastapi.tiangolo.com)
- [Flask Documentation](https://flask.palletsprojects.com)
- [psutil Documentation](https://psutil.readthedocs.io)

## 🎨 Funcionalidades del Dashboard

### Páginas Disponibles

1. **Dashboard** (`/`) - Resumen general del sistema
2. **Proyectos** (`/proyectos`) - Lista y gestión de proyectos
3. **Generar** (`/generar`) - Crear nuevos proyectos Flask
4. **Puertos** (`/puertos`) - Monitor de puertos del sistema
5. **Git** (`/git`) - Estado de repositorios
6. **Sistema** (`/sistema`) - Monitor de recursos

## 🤝 Contribuir

Para más detalles técnicos, ver `CLAUDE.md` y `ORION_GUIDE.md`.

---

**ORION** - Sistema completo de gestión de proyectos Flask
*Desarrollado con FastAPI, Flask y Python*
