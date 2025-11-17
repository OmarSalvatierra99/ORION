"""
ORION Project Generator Module
Generador de proyectos Flask con plantillas completas
"""

import os
import subprocess
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime


class ProjectGenerator:
    """Generador de proyectos Flask con estructura estándar"""

    def __init__(self, portfolio_path: str = "portfolio/projects"):
        self.portfolio_path = Path(portfolio_path)
        self.portfolio_path.mkdir(parents=True, exist_ok=True)

    def create_flask_project(
        self,
        project_name: str,
        port: int,
        description: str = "",
        with_database: bool = False,
        with_api: bool = True,
        with_templates: bool = True
    ) -> Dict:
        """
        Crear un nuevo proyecto Flask con estructura completa

        Args:
            project_name: Nombre del proyecto (sin espacios, minúsculas)
            port: Puerto en el que correrá el proyecto
            description: Descripción del proyecto
            with_database: Incluir SQLite y SQLAlchemy
            with_api: Incluir endpoints de API
            with_templates: Incluir sistema de templates Jinja2

        Returns:
            Diccionario con resultado de la operación
        """
        try:
            # Validar nombre del proyecto
            project_name = project_name.lower().replace(" ", "-")
            project_path = self.portfolio_path / project_name

            if project_path.exists():
                return {
                    "success": False,
                    "error": f"El proyecto '{project_name}' ya existe"
                }

            # Crear estructura de directorios
            project_path.mkdir(parents=True)

            if with_templates:
                (project_path / "templates").mkdir()
                (project_path / "static" / "css").mkdir(parents=True)
                (project_path / "static" / "js").mkdir(parents=True)

            (project_path / "logs").mkdir()

            # Crear archivos principales
            self._create_app_file(project_path, project_name, port, with_database, with_api, with_templates)
            self._create_requirements(project_path, with_database, with_templates)
            self._create_gitignore(project_path)
            self._create_readme(project_path, project_name, port, description)

            if with_database:
                self._create_models_file(project_path, project_name)

            if with_templates:
                self._create_base_template(project_path, project_name)
                self._create_index_template(project_path, project_name)

            # Crear entorno virtual
            self._create_virtualenv(project_path)

            # Inicializar repositorio Git
            self._init_git_repo(project_path, project_name)

            return {
                "success": True,
                "project_name": project_name,
                "project_path": str(project_path),
                "port": port,
                "message": f"Proyecto '{project_name}' creado exitosamente"
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def _create_app_file(self, project_path: Path, name: str, port: int, with_db: bool, with_api: bool, with_templates: bool):
        """Crear archivo app.py principal"""
        imports = ["from flask import Flask"]

        if with_templates:
            imports.append("from flask import render_template, request, redirect, url_for")
        if with_api:
            imports.append("from flask import jsonify")
        if with_db:
            imports.append("from flask_sqlalchemy import SQLAlchemy")

        imports.append("from datetime import datetime")
        imports.append("import os")

        # Agregar imports de ORION
        imports.append("\n# ORION Integration")
        imports.append("import sys")
        imports.append("sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))")
        imports.append("from orion_logger import get_logger")

        app_content = "\n".join(imports) + "\n\n"

        # Configuración
        app_content += "# Configuración\n"
        app_content += "app = Flask(__name__)\n"
        app_content += f"app.config['SECRET_KEY'] = '{os.urandom(24).hex()}'\n"

        if with_db:
            app_content += f"app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///{name}.db'\n"
            app_content += "app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False\n"
            app_content += "db = SQLAlchemy(app)\n\n"

        # Logger
        app_content += f"# ORION Logger\nlogger = get_logger('{name}')\n\n"

        # Rutas básicas
        app_content += "# ==================== RUTAS ====================\n\n"
        app_content += "@app.route('/')\n"
        app_content += "def index():\n"

        if with_templates:
            app_content += f"    logger.info('Página de inicio accedida')\n"
            app_content += f"    return render_template('index.html', project_name='{name}')\n\n"
        else:
            app_content += f"    return '{name.upper()} - Proyecto Flask'\n\n"

        if with_api:
            app_content += "@app.route('/api/status')\n"
            app_content += "def api_status():\n"
            app_content += "    return jsonify({\n"
            app_content += f"        'project': '{name}',\n"
            app_content += "        'status': 'online',\n"
            app_content += "        'timestamp': datetime.utcnow().isoformat()\n"
            app_content += "    })\n\n"

        # Main
        app_content += "if __name__ == '__main__':\n"
        app_content += f"    logger.log_startup('0.0.0.0', {port})\n"
        app_content += f"    app.run(host='0.0.0.0', port={port}, debug=True)\n"

        (project_path / "app.py").write_text(app_content)

    def _create_models_file(self, project_path: Path, name: str):
        """Crear archivo models.py con ejemplo de modelo"""
        models_content = f"""from app import db
from datetime import datetime


class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.Text)
    creado_en = db.Column(db.DateTime, default=datetime.utcnow)
    actualizado_en = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {{
            'id': self.id,
            'nombre': self.nombre,
            'descripcion': self.descripcion,
            'creado_en': self.creado_en.isoformat() if self.creado_en else None,
            'actualizado_en': self.actualizado_en.isoformat() if self.actualizado_en else None
        }}

    def __repr__(self):
        return f'<Item {{self.nombre}}>'


# Crear tablas
if __name__ == '__main__':
    from app import app
    with app.app_context():
        db.create_all()
        print('Base de datos creada exitosamente')
"""
        (project_path / "models.py").write_text(models_content)

    def _create_requirements(self, project_path: Path, with_db: bool, with_templates: bool):
        """Crear requirements.txt"""
        requirements = [
            "Flask==3.0.0",
            "python-dotenv==1.0.0"
        ]

        if with_db:
            requirements.extend([
                "Flask-SQLAlchemy==3.1.1",
                "SQLAlchemy==2.0.23"
            ])

        requirements_text = "\n".join(requirements) + "\n"
        (project_path / "requirements.txt").write_text(requirements_text)

    def _create_gitignore(self, project_path: Path):
        """Crear .gitignore"""
        gitignore_content = """# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
env/
ENV/
*.egg-info/
dist/
build/

# Flask
instance/
.webassets-cache

# Database
*.db
*.sqlite

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Logs
logs/
*.log

# Environment
.env
.env.local
"""
        (project_path / ".gitignore").write_text(gitignore_content)

    def _create_readme(self, project_path: Path, name: str, port: int, description: str):
        """Crear README.md"""
        readme_content = f"""# {name.upper()}

{description or f'Proyecto Flask - {name}'}

## Descripción

Este proyecto fue generado automáticamente por ORION.

## Instalación

```bash
# Crear entorno virtual
python -m venv venv

# Activar entorno virtual
source venv/bin/activate  # Linux/Mac
# o
venv\\Scripts\\activate  # Windows

# Instalar dependencias
pip install -r requirements.txt
```

## Uso

```bash
# Ejecutar la aplicación
python app.py
```

La aplicación estará disponible en: http://localhost:{port}

## Estructura del Proyecto

```
{name}/
├── app.py              # Aplicación principal
├── requirements.txt    # Dependencias
├── templates/          # Templates HTML
├── static/            # Archivos estáticos (CSS, JS)
└── logs/              # Logs de la aplicación
```

## Integración con ORION

Este proyecto está integrado con el sistema ORION de gestión de proyectos.
Los logs se registran automáticamente en formato JSON.

## Desarrollado con

- Flask 3.0.0
- ORION Logging System

---

Generado por ORION - {datetime.now().strftime('%Y-%m-%d')}
"""
        (project_path / "README.md").write_text(readme_content)

    def _create_base_template(self, project_path: Path, name: str):
        """Crear template base.html"""
        base_template = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{% block title %}}{name.upper()}{{% endblock %}}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 10px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            padding: 40px;
        }}
        h1 {{
            color: #667eea;
            margin-bottom: 20px;
        }}
        {{% block styles %}}{{% endblock %}}
    </style>
</head>
<body>
    <div class="container">
        {{% block content %}}{{% endblock %}}
    </div>
    {{% block scripts %}}{{% endblock %}}
</body>
</html>
"""
        (project_path / "templates" / "base.html").write_text(base_template)

    def _create_index_template(self, project_path: Path, name: str):
        """Crear template index.html"""
        index_template = f"""{{% extends "base.html" %}}

{{% block content %}}
<h1>¡Bienvenido a {name.upper()}!</h1>
<p>Este es un proyecto Flask generado por ORION.</p>

<div style="margin-top: 30px; padding: 20px; background: #f0f0f0; border-radius: 5px;">
    <h2>Próximos pasos:</h2>
    <ol style="margin-left: 20px; margin-top: 10px; line-height: 2;">
        <li>Edita <code>app.py</code> para agregar tus rutas</li>
        <li>Personaliza las plantillas en <code>templates/</code></li>
        <li>Agrega estilos en <code>static/css/</code></li>
        <li>Consulta el README.md para más información</li>
    </ol>
</div>

<div style="margin-top: 20px; padding: 15px; background: #e7f3ff; border-left: 4px solid #2196F3; border-radius: 3px;">
    <strong>Integrado con ORION:</strong> Los logs se registran automáticamente en el sistema centralizado.
</div>
{{% endblock %}}
"""
        (project_path / "templates" / "index.html").write_text(index_template)

    def _create_virtualenv(self, project_path: Path):
        """Crear entorno virtual"""
        try:
            subprocess.run(
                ["python", "-m", "venv", "venv"],
                cwd=project_path,
                capture_output=True,
                timeout=60
            )
        except Exception:
            pass  # No crítico si falla

    def _init_git_repo(self, project_path: Path, name: str):
        """Inicializar repositorio Git"""
        try:
            subprocess.run(
                ["git", "init"],
                cwd=project_path,
                capture_output=True,
                timeout=10
            )
            subprocess.run(
                ["git", "add", "."],
                cwd=project_path,
                capture_output=True,
                timeout=10
            )
            subprocess.run(
                ["git", "commit", "-m", f"Proyecto inicial {name} generado por ORION"],
                cwd=project_path,
                capture_output=True,
                timeout=10
            )
        except Exception:
            pass  # No crítico si falla

    def get_available_ports(self, start_port: int = 4000, end_port: int = 6000) -> List[int]:
        """Obtener lista de puertos disponibles en un rango"""
        from orion_system import PortMonitor

        used_ports = {p['port'] for p in PortMonitor.get_listening_ports()}
        available = []

        for port in range(start_port, end_port):
            if port not in used_ports:
                available.append(port)

        return available[:20]  # Primeros 20 disponibles

    def suggest_port(self) -> int:
        """Sugerir un puerto disponible"""
        available = self.get_available_ports()
        return available[0] if available else 5000


if __name__ == "__main__":
    # Ejemplo de uso
    generator = ProjectGenerator()

    result = generator.create_flask_project(
        project_name="mi-proyecto-test",
        port=5100,
        description="Proyecto de prueba generado por ORION",
        with_database=True,
        with_api=True,
        with_templates=True
    )

    print(result)
