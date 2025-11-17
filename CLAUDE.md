# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

ORION is a centralized system for managing cloud-based software projects. It's a FastAPI-based web application that provides:

- **Project Management**: Monitor and manage multiple Flask/FastAPI projects from your portfolio
- **Centralized Logging**: JSON-formatted logging system for all portfolio projects
- **Project Monitoring**: Track project status, health, and activity in real-time
- **Dashboard & API**: Modern, elegant web UI and RESTful API for comprehensive system monitoring
- **Homogeneous Structure**: Maintain consistent structure and standards across all portfolio projects

## Development Commands

### Running ORION

```bash
# Activate virtual environment
source venv/bin/activate

# Start the application (runs on port 4090)
python app.py

# Alternative: Run with uvicorn directly
uvicorn app:app --host 0.0.0.0 --port 4090
```

### Database Initialization

```bash
# Initialize database and auto-discover portfolio projects
python orion_db.py

# This creates orion.db and registers all projects from portfolio/projects/
```

### Testing the Logger

```bash
# Test the logging system
python orion_logger.py

# View logs in real-time (requires jq)
tail -f logs/orion.log | jq .
```

## Architecture

### Core Components

**app.py** (FastAPI Application)
- Main web application with HTML templates (Jinja2) and JSON API endpoints
- Routes for projects (`/proyectos`, `/proyecto/{nombre}/logs`, `/proyecto/{nombre}/detalle`) and API (`/api/*`)
- Startup event auto-initializes portfolio projects from `portfolio/projects/`
- Modern, elegant UI with futuristic dark theme and responsive layouts
- Runs on port 4090

**orion_db.py** (Database Manager)
- SQLite database manager with context manager pattern for connections
- Two main tables: `proyectos`, `actividad_proyectos`
- `OrionDB` class provides methods for CRUD operations on projects
- `inicializar_proyectos_portfolio()` auto-discovers projects from filesystem

**orion_logger.py** (Centralized Logging)
- `OrionLogger` class wraps Python's logging with JSON formatting
- All logs stored in `/logs/{project_name}.log` with structured JSON format
- Provides specialized methods: `log_request()`, `log_startup()`, `log_error_exception()`
- `read_logs()` function parses JSON logs for web display

### Database Schema

**proyectos table**
- Tracks portfolio projects with fields: `nombre`, `ruta`, `puerto`, `estado`, `tipo`, `tecnologias`
- States: `activo`, `detenido`, `error`, `mantenimiento`
- Auto-discovered from `portfolio/projects/` directory
- Timestamps: `creado_en`, `actualizado_en`, `ultima_actividad`

**actividad_proyectos table**
- Event log for project lifecycle events (state changes, deployments, errors, etc.)
- Linked to `proyectos` via `proyecto_id` foreign key
- Fields: `tipo_evento`, `descripcion`, `datos_extra`, `timestamp`
- Useful for tracking project health and historical data

### Portfolio Projects Integration

Portfolio projects are stored in `portfolio/projects/` with these known projects:
- **scil** (port 4050): Flask, pandas, SQLite
- **chat** (port 5002): Flask, SQLAlchemy, SocketIO
- **cleandoc** (port 4085): Flask, python-docx
- **lexnum** (port 4055): Flask, pandas, openpyxl
- **procesar-xml** (port 4080): Flask, pandas, defusedxml
- **scan-actas** (port 5045): Flask, OpenCV, PyMuPDF
- **sipac** (port 5020): Flask, PostgreSQL, pandas

Projects can integrate ORION logging:
```python
from orion_logger import get_logger

logger = get_logger("project_name")
logger.log_startup("0.0.0.0", 5000)
logger.log_request(request.method, request.path, 200)
```

## Key Technical Patterns

### Database Context Manager
All database operations use `OrionDB.get_connection()` context manager which:
- Creates connection with `sqlite3.Row` factory
- Auto-commits on success
- Auto-rolls back on exceptions
- Always closes connection

### JSON Logging Format
All logs use structured JSON with these standard fields:
- `timestamp` (ISO 8601 with 'Z' suffix)
- `level` (INFO, WARNING, ERROR, CRITICAL)
- `project` (logger name: "orion.{project_name}")
- `message` (human-readable message)
- Additional contextual fields via `**extra` kwargs

### Project Auto-Discovery
`inicializar_proyectos_portfolio()` scans `portfolio/projects/` and registers projects based on hardcoded mapping in `orion_db.py:393-403`. To add new projects, update the `proyectos_info` dictionary.

## API Endpoints

**Status and Monitoring**
- `GET /` - Dashboard with system statistics and recent projects
- `GET /api/status` - System status with detailed project statistics (JSON)
- `GET /api/proyectos` - List all projects as JSON
- `GET /api/logs/{proyecto}?limit=100` - Get project logs in JSON format

**Project Management**
- `GET /proyectos` - Web UI for comprehensive project management
- `GET /proyecto/{nombre}/logs` - View logs for specific project
- `GET /proyecto/{nombre}/detalle` - Detailed project view with activity history
- `POST /api/proyecto/{nombre}/estado` - Update project state (form-encoded: `estado=activo`)

## File Structure

```
/home/gabo/ORION/
├── app.py                  # FastAPI application
├── orion_db.py            # Database manager (SQLite)
├── orion_logger.py        # Centralized logging system
├── orion.db               # SQLite database
├── logs/                  # JSON logs for all projects
├── templates/             # Jinja2 HTML templates
│   ├── index.html         # Dashboard
│   ├── proyectos.html     # Project management
│   ├── proyecto_logs.html # Log viewer
│   └── proyecto_detalle.html # Project details (if exists)
├── static/                # Static assets
│   ├── css/
│   │   └── style.css      # Main stylesheet
│   └── js/
│       └── app.js         # Frontend logic
├── portfolio/projects/    # Portfolio projects directory
└── venv/                  # Python virtual environment
```

## Working with ORION

### Adding a New Portfolio Project

1. Update `proyectos_info` dictionary in `orion_db.py` (around line 393)
2. Run `python orion_db.py` to register the new project
3. Integrate logging in the project's main file (see ORION_GUIDE.md)

### Querying Database Directly

```bash
sqlite3 orion.db

# Useful queries
SELECT nombre, puerto, estado FROM proyectos WHERE estado = 'activo';
SELECT descripcion, (monto - pagado) as saldo FROM deudas WHERE estado != 'pagada';
```

### Debugging Issues

- Check ORION logs: `logs/orion.log`
- Check specific project logs: `logs/{project_name}.log`
- Verify database state: `sqlite3 orion.db ".tables"` and `.schema`
- Check port availability: `lsof -i :4090`

## Environment

- **Python Version**: 3.13
- **Web Framework**: FastAPI 0.104.1 with Uvicorn 0.24.0
- **Database**: SQLite (file-based, `orion.db`)
- **Port**: 4090 (hardcoded in `app.py`)
- **Logs Directory**: `/home/gabo/ORION/logs/`

## Design Philosophy

ORION follows a clean, functional, and elegant design approach:

### Visual Design
- **Dark futuristic theme**: Inspired by AI assistant interfaces like Jarvis
- **Color palette**: Electric blue (`#00d4ff`), dark backgrounds, glowing effects
- **Smooth animations**: Subtle transitions and hover effects for better UX
- **Responsive layout**: Works seamlessly across desktop and mobile devices

### Code Standards
- **Centralized logging**: All projects use the same JSON logging format
- **Database-driven**: SQLite for lightweight but robust data persistence
- **RESTful API**: Clean API design for programmatic access
- **Modular architecture**: Separation of concerns (DB, logging, web layer)

## Templates

**index.html** - Modern dashboard with futuristic dark theme showing:
- System statistics (active projects, total projects, alerts, logs)
- Recent projects with status badges
- Quick action buttons for common tasks
- Animated ORION logo with pulsing rings

**proyectos.html** - Comprehensive project management interface with:
- Grid layout of all projects with status indicators
- Technology stack badges
- Quick access to logs and project details
- Elegant card-based design with hover effects

**proyecto_logs.html** - Log viewer for individual projects with:
- JSON log parsing and formatting
- Color-coded log levels (INFO, WARNING, ERROR)
- Pagination and filtering capabilities

**proyecto_detalle.html** - Detailed project view with:
- Complete project information
- Activity history timeline
- Recent logs preview
- Project health indicators

All templates use a cohesive dark futuristic theme with electric blue accents, smooth animations, and responsive layouts
