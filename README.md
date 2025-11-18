# ORION v3.0

Sistema minimalista de gestión de proyectos.

## Características

- **Lista de proyectos** - Vista simple de todos tus proyectos
- **Control de procesos** - Inicia, detiene y reinicia proyectos
- **Monitoreo** - Puerto, CPU, memoria y PID en tiempo real
- **Logs** - Historial de eventos de cada proyecto
- **Git** - Estado del repositorio y archivos modificados

## Instalación

```bash
pip install -r requirements.txt
```

## Uso

```bash
python app.py
```

Accede a `http://localhost:4090`

## Estructura

```
ORION/
├── app.py                 # Aplicación principal
├── config.py              # Configuración
├── core/                  # Funcionalidad core
│   ├── database.py        # SQLite
│   ├── logger.py          # Logs
│   └── project_manager.py # Gestión de proyectos
├── services/              # Servicios
│   ├── git_service.py     # Git integration
│   └── system_monitor.py  # Monitoreo
├── routers/               # Endpoints
│   ├── projects.py        # Proyectos
│   └── api.py             # API REST
├── templates/             # Vistas HTML
└── static/                # CSS/JS
```

## API

- `GET /` - Lista de proyectos
- `GET /proyecto/{nombre}/detalle` - Detalle del proyecto (puerto, logs, git)
- `GET /proyecto/{nombre}/logs` - Logs completos
- `POST /proyecto/{nombre}/start` - Iniciar proyecto
- `POST /proyecto/{nombre}/stop` - Detener proyecto
- `POST /proyecto/{nombre}/restart` - Reiniciar proyecto

## Licencia

MIT
