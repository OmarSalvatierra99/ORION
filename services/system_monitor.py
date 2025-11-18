"""
ORION System Monitor Module
Monitoreo de puertos, rendimiento, CPU, memoria y procesos
"""

import psutil
import subprocess
from typing import Dict, List, Optional
from datetime import datetime
import os


class SystemMonitor:
    """Monitor de recursos y estado del sistema"""

    @staticmethod
    def get_cpu_info() -> Dict:
        """Información de CPU"""
        return {
            "percent": psutil.cpu_percent(interval=1),
            "count": psutil.cpu_count(),
            "count_physical": psutil.cpu_count(logical=False),
            "freq": psutil.cpu_freq()._asdict() if psutil.cpu_freq() else None,
        }

    @staticmethod
    def get_memory_info() -> Dict:
        """Información de memoria"""
        mem = psutil.virtual_memory()
        swap = psutil.swap_memory()

        return {
            "total": mem.total,
            "available": mem.available,
            "used": mem.used,
            "percent": mem.percent,
            "total_gb": round(mem.total / (1024**3), 2),
            "used_gb": round(mem.used / (1024**3), 2),
            "available_gb": round(mem.available / (1024**3), 2),
            "swap": {
                "total": swap.total,
                "used": swap.used,
                "percent": swap.percent,
            }
        }

    @staticmethod
    def get_disk_info() -> List[Dict]:
        """Información de discos"""
        disks = []
        for partition in psutil.disk_partitions():
            try:
                usage = psutil.disk_usage(partition.mountpoint)
                disks.append({
                    "device": partition.device,
                    "mountpoint": partition.mountpoint,
                    "fstype": partition.fstype,
                    "total_gb": round(usage.total / (1024**3), 2),
                    "used_gb": round(usage.used / (1024**3), 2),
                    "free_gb": round(usage.free / (1024**3), 2),
                    "percent": usage.percent,
                })
            except PermissionError:
                continue
        return disks

    @staticmethod
    def get_network_info() -> Dict:
        """Información de red"""
        net_io = psutil.net_io_counters()
        return {
            "bytes_sent": net_io.bytes_sent,
            "bytes_recv": net_io.bytes_recv,
            "bytes_sent_mb": round(net_io.bytes_sent / (1024**2), 2),
            "bytes_recv_mb": round(net_io.bytes_recv / (1024**2), 2),
            "packets_sent": net_io.packets_sent,
            "packets_recv": net_io.packets_recv,
        }

    @staticmethod
    def get_system_uptime() -> Dict:
        """Tiempo de actividad del sistema"""
        boot_time = datetime.fromtimestamp(psutil.boot_time())
        uptime = datetime.now() - boot_time

        return {
            "boot_time": boot_time.isoformat(),
            "uptime_seconds": int(uptime.total_seconds()),
            "uptime_str": str(uptime).split('.')[0],  # Remover microsegundos
        }


class PortMonitor:
    """Monitor de puertos en uso"""

    @staticmethod
    def get_listening_ports() -> List[Dict]:
        """Obtener todos los puertos en escucha"""
        ports = []
        for conn in psutil.net_connections(kind='inet'):
            if conn.status == 'LISTEN':
                try:
                    process = psutil.Process(conn.pid) if conn.pid else None
                    ports.append({
                        "port": conn.laddr.port,
                        "address": conn.laddr.ip,
                        "pid": conn.pid,
                        "process": process.name() if process else "unknown",
                        "cmdline": " ".join(process.cmdline()) if process else "",
                    })
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    ports.append({
                        "port": conn.laddr.port,
                        "address": conn.laddr.ip,
                        "pid": conn.pid,
                        "process": "unknown",
                        "cmdline": "",
                    })

        # Ordenar por puerto
        return sorted(ports, key=lambda x: x['port'])

    @staticmethod
    def get_project_ports(projects_info: List[Dict]) -> List[Dict]:
        """Cruzar puertos de proyectos con puertos en uso"""
        listening_ports = {p['port']: p for p in PortMonitor.get_listening_ports()}

        project_ports = []
        for project in projects_info:
            port = project.get('puerto')
            if port:
                is_active = port in listening_ports
                port_info = listening_ports.get(port, {})

                project_ports.append({
                    "project": project.get('nombre'),
                    "port": port,
                    "is_active": is_active,
                    "process": port_info.get('process'),
                    "pid": port_info.get('pid'),
                })

        return sorted(project_ports, key=lambda x: x['port'])

    @staticmethod
    def check_port_available(port: int) -> bool:
        """Verificar si un puerto está disponible"""
        listening_ports = {p['port'] for p in PortMonitor.get_listening_ports()}
        return port not in listening_ports


class ProcessMonitor:
    """Monitor de procesos del sistema"""

    @staticmethod
    def get_top_processes(limit: int = 10, sort_by: str = 'cpu') -> List[Dict]:
        """Obtener procesos principales por CPU o memoria"""
        processes = []

        for proc in psutil.process_iter(['pid', 'name', 'username', 'cpu_percent', 'memory_percent']):
            try:
                pinfo = proc.info
                processes.append({
                    "pid": pinfo['pid'],
                    "name": pinfo['name'],
                    "username": pinfo['username'],
                    "cpu_percent": pinfo['cpu_percent'],
                    "memory_percent": round(pinfo['memory_percent'], 2),
                })
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass

        # Ordenar por criterio
        if sort_by == 'cpu':
            processes.sort(key=lambda x: x['cpu_percent'], reverse=True)
        else:
            processes.sort(key=lambda x: x['memory_percent'], reverse=True)

        return processes[:limit]

    @staticmethod
    def get_process_count() -> int:
        """Contar procesos activos"""
        return len(psutil.pids())


def get_system_summary() -> Dict:
    """Obtener resumen completo del sistema"""
    monitor = SystemMonitor()

    return {
        "timestamp": datetime.now().isoformat(),
        "cpu": monitor.get_cpu_info(),
        "memory": monitor.get_memory_info(),
        "disk": monitor.get_disk_info(),
        "network": monitor.get_network_info(),
        "uptime": monitor.get_system_uptime(),
        "process_count": ProcessMonitor.get_process_count(),
        "listening_ports_count": len(PortMonitor.get_listening_ports()),
    }
