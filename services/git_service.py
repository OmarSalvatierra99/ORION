"""
ORION Git Integration Module
Manejo de repositorios Git, .gitignore y comparaciones con GitHub
"""

import os
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import json


class GitManager:
    """Gestor de operaciones Git para proyectos"""

    def __init__(self, project_path: str):
        self.project_path = Path(project_path)
        self.git_dir = self.project_path / ".git"

    def is_git_repo(self) -> bool:
        """Verificar si el directorio es un repositorio Git"""
        return self.git_dir.exists() and self.git_dir.is_dir()

    def get_git_status(self) -> Dict:
        """Obtener estado actual del repositorio"""
        if not self.is_git_repo():
            return {"error": "Not a git repository"}

        try:
            # Branch actual
            branch = self._run_git_command(["git", "branch", "--show-current"])

            # Commits locales adelante/atrás del remoto
            remote_status = self._run_git_command(["git", "status", "-sb"])

            # Archivos modificados
            modified = self._run_git_command(["git", "status", "--porcelain"])

            # Último commit
            last_commit = self._run_git_command(
                ["git", "log", "-1", "--pretty=format:%h - %s (%cr)"]
            )

            # URL remota
            remote_url = self._run_git_command(
                ["git", "config", "--get", "remote.origin.url"]
            )

            return {
                "branch": branch.strip(),
                "remote_url": remote_url.strip() if remote_url else None,
                "remote_status": remote_status.strip(),
                "modified_files": self._parse_modified_files(modified),
                "last_commit": last_commit.strip() if last_commit else None,
                "is_clean": len(modified.strip()) == 0,
            }
        except Exception as e:
            return {"error": str(e)}

    def get_gitignore(self) -> Optional[str]:
        """Leer contenido del archivo .gitignore"""
        gitignore_path = self.project_path / ".gitignore"
        if gitignore_path.exists():
            try:
                return gitignore_path.read_text()
            except Exception as e:
                return f"Error reading .gitignore: {e}"
        return None

    def get_remote_comparison(self) -> Dict:
        """Comparar con el repositorio remoto"""
        if not self.is_git_repo():
            return {"error": "Not a git repository"}

        try:
            # Fetch para obtener última info del remoto
            self._run_git_command(["git", "fetch"])

            # Commits adelante del remoto
            ahead = self._run_git_command(
                ["git", "rev-list", "--count", "HEAD@{upstream}..HEAD"]
            )

            # Commits atrás del remoto
            behind = self._run_git_command(
                ["git", "rev-list", "--count", "HEAD..HEAD@{upstream}"]
            )

            return {
                "ahead": int(ahead.strip()) if ahead.strip().isdigit() else 0,
                "behind": int(behind.strip()) if behind.strip().isdigit() else 0,
            }
        except Exception as e:
            return {"error": str(e)}

    def get_recent_commits(self, limit: int = 10) -> List[Dict]:
        """Obtener commits recientes"""
        if not self.is_git_repo():
            return []

        try:
            commits_raw = self._run_git_command([
                "git", "log",
                f"-{limit}",
                "--pretty=format:%h|%an|%ar|%s"
            ])

            commits = []
            for line in commits_raw.split("\n"):
                if line.strip():
                    parts = line.split("|")
                    if len(parts) == 4:
                        commits.append({
                            "hash": parts[0],
                            "author": parts[1],
                            "time": parts[2],
                            "message": parts[3]
                        })
            return commits
        except Exception:
            return []

    def get_branches(self) -> List[str]:
        """Listar todas las branches"""
        if not self.is_git_repo():
            return []

        try:
            branches_raw = self._run_git_command(["git", "branch", "-a"])
            branches = []
            for line in branches_raw.split("\n"):
                line = line.strip()
                if line:
                    # Remover asterisco de branch actual
                    branch = line.replace("* ", "")
                    branches.append(branch)
            return branches
        except Exception:
            return []

    def _run_git_command(self, command: List[str]) -> str:
        """Ejecutar comando Git y retornar output"""
        try:
            result = subprocess.run(
                command,
                cwd=self.project_path,
                capture_output=True,
                text=True,
                timeout=10
            )
            return result.stdout
        except subprocess.TimeoutExpired:
            return ""
        except Exception:
            return ""

    def _parse_modified_files(self, status_output: str) -> List[Dict]:
        """Parsear archivos modificados del status"""
        files = []
        for line in status_output.split("\n"):
            if line.strip():
                # Formato: XY filename
                status_code = line[:2]
                filename = line[3:].strip()
                files.append({
                    "file": filename,
                    "status": self._interpret_status(status_code)
                })
        return files

    def _interpret_status(self, code: str) -> str:
        """Interpretar código de estado de Git"""
        status_map = {
            "M ": "modified",
            " M": "modified",
            "MM": "modified",
            "A ": "added",
            "D ": "deleted",
            "R ": "renamed",
            "C ": "copied",
            "??": "untracked",
        }
        return status_map.get(code, "unknown")


def scan_portfolio_git_repos(portfolio_path: str = "portfolio/projects") -> List[Dict]:
    """Escanear todos los proyectos del portfolio y obtener info Git"""
    portfolio_path = Path(portfolio_path)
    repos = []

    if not portfolio_path.exists():
        return repos

    for project_dir in portfolio_path.iterdir():
        if project_dir.is_dir():
            git_manager = GitManager(str(project_dir))
            if git_manager.is_git_repo():
                status = git_manager.get_git_status()
                repos.append({
                    "name": project_dir.name,
                    "path": str(project_dir),
                    "status": status
                })

    return repos


def get_github_username_from_url(url: str) -> Optional[str]:
    """Extraer nombre de usuario de GitHub de URL remota"""
    if "github.com" in url:
        # Formato: git@github.com:username/repo.git o https://github.com/username/repo.git
        parts = url.replace("git@github.com:", "").replace("https://github.com/", "").split("/")
        if parts:
            return parts[0]
    return None
