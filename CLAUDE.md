# CLAUDE.md

This file provides guidance to Claude Code when working with code in this repository.

## Project Overview

**ORION v3.0** is a centralized system for managing cloud-based software projects. It's a modular FastAPI-based application that provides:

- **Project Management**: Auto-discover, monitor, and control Flask/FastAPI projects
- **Process Control**: Start/stop/restart projects directly from the dashboard
- **Dependency Tracking**: Read and display requirements.txt for each project
- **Centralized Logging**: JSON-formatted logging system for all projects
- **Real-time Monitoring**: Track CPU, memory, ports, and project health
- **RESTful API**: Complete API for programmatic access
- **Modern Dashboard**: Elegant UI with futuristic dark theme

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run ORION (port 4090)
python app.py

# Alternative with uvicorn
uvicorn app:app --host 0.0.0.0 --port 4090
```

## Architecture

### **Version 3.0 - Modular Structure**

```
ORION/
├── config.py                    # Centralized configuration
├── app.py                       # Minimal FastAPI application
│
├── core/                        # Core functionality
│   ├── database.py             # SQLite database manager
│   ├── logger.py               # JSON logging system
│   └── project_manager.py      # Project control & discovery
│
├── services/                    # Auxiliary services
│   ├── system_monitor.py       # CPU, memory, ports monitoring
│   └── git_service.py          # Git integration
│
├── routers/                     # Route modules
│   ├── projects.py             # Project management routes
│   ├── api.py                  # REST API endpoints
│   └── system.py               # System monitoring routes
│
├── templates/                   # Jinja2 HTML templates
├── static/                      # CSS, JS, images
├── logs/                        # JSON log files
├── portfolio/projects/          # Portfolio projects directory
└── orion.db                     # SQLite database
```

### Key Design Principles

1. **Modular**: Clear separation of concerns (core, services, routers)
2. **Minimal**: Each module has a single, well-defined responsibility
3. **Functional**: Focus on practical features (start/stop, requirements, monitoring)
4. **Clean**: No redundant code, easy to read and maintain

## Core Modules

### **config.py**
Centralized configuration for the entire system:
- Directories (LOGS_DIR, DB_PATH, PORTFOLIO_DIR)
- Application settings (HOST, PORT, VERSION)
- Project states and port ranges

### **core/database.py**
Simplified database manager with context manager pattern:
- `db.add_project()` - Add new project
- `db.get_project(name)` - Get project by name
- `db.list_projects()` - List all projects
- `db.update_project(name, **kwargs)` - Update project fields
- `db.sync_projects(projects)` - Sync discovered projects with DB
- `db.log_activity()` - Log project events

**Database Schema:**
- **proyectos**: id, nombre, ruta, puerto, estado, tipo, tecnologias, dependencies, pid
- **actividad**: id, proyecto_id, tipo_evento, descripcion, timestamp

### **core/logger.py**
Simplified JSON logging system:
- `logger = get_logger(project_name)` - Get logger instance
- `logger.info/warning/error()` - Log messages
- `read_logs(project_name, limit)` - Read project logs
- `get_logs_summary()` - Get summary of all logs

**Log Format:**
```json
{
  "timestamp": "2024-01-15T10:30:00Z",
  "level": "INFO",
  "project": "orion.project_name",
  "message": "Project started",
  "extra_field": "value"
}
```

### **core/project_manager.py** ⭐ NEW
The heart of project management:

**Discovery & Analysis:**
- `discover_projects()` - Auto-discover projects in portfolio directory
- `_analyze_project(path)` - Deep analysis of project structure and app.py
- `_analyze_app_file(app_file, project_type)` - ⭐ Analyze app.py in depth
  - Extracts endpoints/routes (Flask @app.route, FastAPI @app.get/post/etc.)
  - Detects imports and dependencies
  - Identifies features (database, authentication)
  - Extracts description from docstrings
- `read_requirements(path)` - Parse requirements.txt
- `get_requirements_info(name)` - Get detailed dependency info

**What app.py Analysis Detects:**
- 🌐 **Endpoints**: All HTTP routes with methods (GET, POST, PUT, DELETE, etc.)
- 📚 **Imports**: All imported modules and packages
- 📝 **Description**: Docstring from the beginning of the file
- 🔧 **Features**:
  - Database usage (SQLAlchemy, sqlite, mysql, postgres, mongodb)
  - Authentication (JWT, login, session, token)
- 🔌 **Port**: Automatically detected from app.run() or uvicorn.run()
- 🏷️ **Framework**: Flask, FastAPI, Django, or generic Python

**Control:**
- `start_project(name)` - Start project subprocess
- `stop_project(name)` - Stop project by PID
- `restart_project(name)` - Restart project
- `is_project_running(name)` - Check if running

**Status:**
- `get_project_status(name, port)` - Get real-time status (PID, CPU, memory)
- `get_all_project_status()` - Get status of all projects

## Services

### **services/system_monitor.py**
System resource monitoring:
- `SystemMonitor` - CPU, memory, disk, network info
- `PortMonitor` - List listening ports, check port availability
- `ProcessMonitor` - Top processes by CPU/memory

### **services/git_service.py**
Git repository integration:
- `GitManager.get_git_status()` - Repository status
- `GitManager.get_recent_commits()` - Recent commit history
- `GitManager.get_branches()` - List branches

## Routers

### **routers/projects.py**
Project management endpoints:
- `GET /proyectos` - Project list view
- `GET /proyecto/{nombre}/detalle` - Project details with requirements
- `GET /proyecto/{nombre}/logs` - Project logs view
- `POST /proyecto/{nombre}/start` - Start project
- `POST /proyecto/{nombre}/stop` - Stop project
- `POST /proyecto/{nombre}/restart` - Restart project
- `POST /proyectos/sync` - Sync projects from filesystem

### **routers/api.py**
REST API endpoints (all under `/api`):
- `GET /api/status` - System status
- `GET /api/proyectos` - List all projects (JSON)
- `GET /api/proyecto/{nombre}` - Get project info + requirements + analysis
- `GET /api/proyecto/{nombre}/analysis` - ⭐ Get detailed app.py analysis
  - Returns: endpoints, imports, description, features (database, auth)
  - Analyzes Flask routes (@app.route, @app.get/post/etc.)
  - Analyzes FastAPI routes (@app.get/post, @router.get/post/etc.)
- `GET /api/proyecto/{nombre}/logs` - Get project logs (JSON)
- `GET /api/proyecto/{nombre}/status` - Real-time project status
- `GET /api/proyecto/{nombre}/requirements` - Project dependencies

### **routers/system.py**
System monitoring endpoints:
- `GET /sistema` - System dashboard (CPU, memory, processes)
- `GET /puertos` - Ports dashboard (listening ports)
- `GET /api/sistema` - System info (JSON)
- `GET /api/puertos` - Ports info (JSON)
- `GET /api/procesos` - Process info (JSON)

## Main Application

### **app.py**
Minimal FastAPI application:
- Includes all routers
- Startup event: auto-discovers and syncs projects
- Dashboard route (`/`)
- Health check (`/health`)

## Common Tasks

### Start/Stop Projects Programmatically

```python
from core.project_manager import project_manager

# Start a project
result = project_manager.start_project("my-project")
print(result)  # {'success': True, 'pid': 12345}

# Stop a project
result = project_manager.stop_project("my-project")

# Get status
status = project_manager.get_project_status("my-project", port=5000)
print(status)  # {'is_running': True, 'pid': 12345, 'cpu_percent': 2.5}
```

### Work with Database

```python
from core.database import db

# List projects
projects = db.list_projects()

# Get specific project
project = db.get_project("chat")

# Update project
db.update_project("chat", estado="activo", pid=12345)

# Log activity
db.log_activity("chat", "inicio", "Project started successfully")
```

### Read Project Requirements

```python
from core.project_manager import project_manager

# Get requirements info
req_info = project_manager.get_requirements_info("chat")
print(req_info)
# {
#   'exists': True,
#   'dependencies': ['flask', 'sqlalchemy', 'socketio'],
#   'count': 3
# }
```

### Analyze app.py in Depth ⭐ NEW

```python
from core.project_manager import project_manager
from pathlib import Path

# Analyze a specific project
project_path = Path("portfolio/projects/my-api")
analysis = project_manager._analyze_project(project_path)

print(f"Type: {analysis['tipo']}")
print(f"Port: {analysis['puerto']}")
print(f"Description: {analysis['descripcion']}")

# Endpoints discovered
print(f"\nEndpoints ({len(analysis['endpoints'])}):")
for endpoint in analysis['endpoints']:
    print(f"  {endpoint['method']} {endpoint['path']}")

# Imports detected
print(f"\nImports ({len(analysis['imports'])}):")
for imp in analysis['imports'][:10]:
    print(f"  • {imp}")

# Features
print(f"\nFeatures:")
print(f"  Database: {analysis['has_database']}")
print(f"  Authentication: {analysis['has_auth']}")
```

### Auto-Discover Projects

```python
from core.project_manager import project_manager
from core.database import db

# Discover projects from portfolio directory
discovered = project_manager.discover_projects()

# Sync with database
db.sync_projects(discovered)

print(f"Synced {len(discovered)} projects")
```

## API Usage Examples

```bash
# Get system status
curl http://localhost:4090/api/status

# List all projects
curl http://localhost:4090/api/proyectos

# Get project with requirements and analysis
curl http://localhost:4090/api/proyecto/chat

# Get detailed app.py analysis (NEW)
curl http://localhost:4090/api/proyecto/chat/analysis

# Get project logs
curl http://localhost:4090/api/proyecto/chat/logs?limit=50

# Get project status (CPU, memory, PID)
curl http://localhost:4090/api/proyecto/chat/status

# Start a project
curl -X POST http://localhost:4090/proyecto/chat/start

# Stop a project
curl -X POST http://localhost:4090/proyecto/chat/stop

# Sync projects from filesystem
curl -X POST http://localhost:4090/proyectos/sync
```

## Configuration

All configuration is centralized in **config.py**:

```python
# Modify these as needed
APP_HOST = "0.0.0.0"
APP_PORT = 4090
PORTFOLIO_DIR = BASE_DIR / "portfolio" / "projects"
LOG_LEVEL = "INFO"
```

## Project States

Projects can have these states:
- **activo**: Project is running
- **detenido**: Project is stopped
- **error**: Project encountered an error
- **mantenimiento**: Under maintenance

## Database Queries

```bash
sqlite3 orion.db

# List active projects
SELECT nombre, puerto, estado, pid FROM proyectos WHERE estado = 'activo';

# View recent activity
SELECT p.nombre, a.tipo_evento, a.descripcion, a.timestamp
FROM actividad a
JOIN proyectos p ON a.proyecto_id = p.id
ORDER BY a.timestamp DESC LIMIT 20;

# Check dependencies
SELECT nombre, dependencies FROM proyectos WHERE dependencies IS NOT NULL;
```

## Logging

All logs are stored in `logs/` directory in JSON format:

```bash
# View logs in real-time (requires jq)
tail -f logs/orion.log | jq .

# Search for errors
grep -i error logs/orion.log | jq .

# View specific project logs
cat logs/chat.log | jq .
```

## Environment

- **Python**: 3.8+
- **Framework**: FastAPI 0.104.1 + Uvicorn 0.24.0
- **Database**: SQLite (orion.db)
- **Port**: 4090
- **Dependencies**: psutil, jinja2, python-multipart

## Design Philosophy

**v3.0 Goals:**
- ✅ Modular architecture with clear separation
- ✅ Minimalista - no redundant code
- ✅ Functional - practical features that work
- ✅ Clean code - easy to read and maintain
- ✅ Auto-discovery of portfolio projects
- ✅ Start/stop projects directly
- ✅ Read and display requirements.txt
- ✅ Real-time process monitoring
- ✅ Comprehensive REST API

## Troubleshooting

**Import errors:**
```bash
pip install -r requirements.txt
```

**Database issues:**
```bash
# Reset database
rm orion.db
python -c "from core.database import db; print('DB initialized')"
```

**Port conflicts:**
```bash
# Check what's using port 4090
lsof -i :4090
```

**Project won't start:**
- Check if port is available
- Verify project has valid main file (app.py, main.py)
- Check project logs in `logs/{project_name}.log`
