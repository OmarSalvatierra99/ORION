#!/usr/bin/env python3
"""
Script de prueba para verificar integraciones de ORION
"""
import os
import sys
from pathlib import Path


def test_environment():
    """Verifica que el entorno esté configurado correctamente"""
    print("=" * 60)
    print("🔍 Verificando Entorno")
    print("=" * 60)

    # Verificar Python version
    print(f"✓ Python: {sys.version.split()[0]}")

    # Verificar directorio actual
    if Path.cwd().name != "ORION":
        print("⚠ Advertencia: No estás en el directorio ORION")
    else:
        print(f"✓ Directorio: {Path.cwd()}")

    # Verificar archivos esenciales
    files = ["app.py", "orion_db.py", "orion_logger.py", "orion_ai.py"]
    for file in files:
        if Path(file).exists():
            print(f"✓ Archivo encontrado: {file}")
        else:
            print(f"✗ Archivo faltante: {file}")

    print()


def test_openai():
    """Verifica la integración con OpenAI"""
    print("=" * 60)
    print("🤖 Probando Integración OpenAI")
    print("=" * 60)

    # Verificar .env
    env_file = Path(".env")
    if not env_file.exists():
        print("✗ Archivo .env no encontrado")
        print("  Crea un archivo .env con: OPENAI_API_KEY=tu_key")
        return False

    # Cargar .env
    from dotenv import load_dotenv
    load_dotenv()

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("✗ OPENAI_API_KEY no encontrada en .env")
        return False

    print(f"✓ OPENAI_API_KEY encontrada (longitud: {len(api_key)})")

    # Probar importación
    try:
        from orion_ai import get_orion_ai
        print("✓ Módulo orion_ai importado correctamente")
    except ImportError as e:
        print(f"✗ Error al importar orion_ai: {e}")
        print("  Ejecuta: pip install openai python-dotenv")
        return False

    # Probar inicialización
    try:
        ai = get_orion_ai()
        print("✓ OrionAI inicializado correctamente")
    except Exception as e:
        print(f"✗ Error al inicializar OrionAI: {e}")
        return False

    # Probar chat simple
    try:
        print("\n  Probando chat con AI...")
        respuesta = ai.chat("Hola, di 'OK' si funcionas correctamente")
        print(f"  Respuesta: {respuesta[:100]}...")
        print("✓ Chat funcionando correctamente")
        return True
    except Exception as e:
        print(f"✗ Error en chat: {e}")
        return False


def test_database():
    """Verifica la base de datos"""
    print("\n" + "=" * 60)
    print("💾 Probando Base de Datos")
    print("=" * 60)

    db_file = Path("orion.db")
    if not db_file.exists():
        print("⚠ orion.db no encontrado")
        print("  Ejecuta: python orion_db.py")
        return False

    print("✓ orion.db encontrado")

    try:
        from orion_db import OrionDB
        db = OrionDB()
        print("✓ OrionDB inicializado correctamente")

        # Contar proyectos
        proyectos = db.listar_proyectos()
        print(f"✓ Proyectos registrados: {len(proyectos)}")

        # Contar deudas
        deudas = db.listar_deudas()
        print(f"✓ Deudas registradas: {len(deudas)}")

        return True
    except Exception as e:
        print(f"✗ Error con base de datos: {e}")
        return False


def test_server():
    """Verifica que el servidor puede iniciar"""
    print("\n" + "=" * 60)
    print("🚀 Probando Servidor FastAPI")
    print("=" * 60)

    try:
        from app import app
        print("✓ Aplicación FastAPI cargada correctamente")
        print(f"✓ Rutas registradas: {len(app.routes)}")
        return True
    except Exception as e:
        print(f"✗ Error al cargar app: {e}")
        return False


def main():
    """Ejecuta todas las pruebas"""
    print("\n🌟 ORION - Verificador de Integraciones\n")

    results = {
        "Entorno": test_environment(),
        "Base de Datos": test_database(),
        "OpenAI": test_openai(),
        "Servidor": test_server()
    }

    # Resumen
    print("\n" + "=" * 60)
    print("📊 Resumen de Pruebas")
    print("=" * 60)

    for nombre, resultado in results.items():
        status = "✓ PASS" if resultado else "✗ FAIL"
        print(f"{status:8} - {nombre}")

    total_pass = sum(1 for r in results.values() if r)
    total = len(results)

    print(f"\nResultado: {total_pass}/{total} pruebas pasadas")

    if total_pass == total:
        print("\n🎉 ¡Todas las integraciones están funcionando correctamente!")
        print("\nPuedes iniciar ORION con: python app.py")
    else:
        print("\n⚠ Algunas integraciones necesitan configuración.")
        print("Ver README.md para instrucciones detalladas.")

    return total_pass == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
