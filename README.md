# 🌟 ORION - Asistente Virtual Inteligente

Sistema centralizado de gestión de proyectos y finanzas personales con **Inteligencia Artificial**.

## 🚀 Características Principales

### 📊 Gestión de Proyectos
- Monitoreo centralizado de proyectos del portfolio
- Sistema de logs en formato JSON
- Control de estados (activo, detenido, error, mantenimiento)
- Dashboard con estadísticas en tiempo real

### 💰 Gestión Financiera con AI
- **Análisis Inteligente de Deudas** powered by OpenAI GPT-4
- Generación automática de planes de pago optimizados
- Recomendaciones financieras personalizadas
- Control de pagos y saldos
- Alertas de vencimientos

### 💬 Asistente AI
- Chat inteligente con contexto del sistema
- Análisis de logs y debugging asistido
- Sugerencias de optimización

## 📦 Instalación

### 1. Clonar y configurar entorno

```bash
cd /home/gabo/ORION
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Configurar Variables de Entorno

Crea un archivo `.env` en la raíz del proyecto:

```env
# OpenAI API Key (Requerido para funcionalidades AI)
OPENAI_API_KEY=tu_api_key_aqui
```

**Obtener OpenAI API Key:**
1. Ir a https://platform.openai.com/api-keys
2. Crear una nueva API key
3. Copiar y pegar en `.env`

### 3. Inicializar Base de Datos

```bash
python orion_db.py
```

Esto creará:
- Base de datos SQLite (`orion.db`)
- Registrará proyectos del portfolio
- Inicializará tablas de deudas y actividad

### 4. Ejecutar ORION

```bash
python app.py
```

ORION estará disponible en: **http://localhost:4090**

## 🎯 Uso de Funcionalidades AI

### Análisis de Deudas con AI

1. Ir a http://localhost:4090/deudas
2. Click en **"🤖 Análisis AI"**
3. Ver análisis completo con:
   - Evaluación de situación financiera
   - Priorización de pagos (método avalancha/bola de nieve)
   - Recomendaciones accionables
   - Alertas de deudas vencidas

### Plan de Pagos Inteligente

1. En la tabla de deudas, click en **"Plan 📋"** en cualquier deuda
2. La AI generará automáticamente:
   - Plazo recomendado
   - Monto mensual sugerido
   - Calendario de pagos detallado
   - Consejos personalizados

### Chat con Asistente AI

```bash
curl -X POST http://localhost:4090/api/chat \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "mensaje=¿Cómo puedo optimizar el pago de mis deudas?"
```

## 🛠️ API Endpoints

### Endpoints AI

```bash
# Obtener análisis de deudas
GET /deudas/analisis

# Generar plan de pago para una deuda
GET /deudas/{deuda_id}/plan-pago

# Chat con AI
POST /api/chat
  Body: mensaje=tu_pregunta_aqui
```

### Endpoints de Sistema

```bash
# Estado del sistema
GET /api/status

# Listar proyectos
GET /api/proyectos

# Listar deudas
GET /api/deudas

# Logs de proyecto
GET /api/logs/{proyecto}?limit=100
```

## 📁 Estructura del Proyecto

```
/home/gabo/ORION/
├── app.py                      # FastAPI app principal
├── orion_db.py                 # Gestor de base de datos
├── orion_logger.py             # Sistema de logging
├── orion_ai.py                 # 🆕 Integración OpenAI
├── .env                        # Variables de entorno
├── orion.db                    # Base de datos SQLite
├── logs/                       # Logs JSON de proyectos
├── templates/                  # Templates HTML
│   ├── deudas.html            # Vista principal de deudas
│   ├── deudas_analisis.html   # 🆕 Análisis AI
│   └── plan_pago.html         # 🆕 Plan de pagos
├── static/                     # Archivos estáticos
├── portfolio/projects/         # Proyectos del portfolio
└── venv/                       # Entorno virtual
```

## 🔧 Configuración Avanzada

### Cambiar modelo de OpenAI

Editar `orion_ai.py`:
```python
self.model = "gpt-4"  # Para análisis más profundos
# o
self.model = "gpt-4o-mini"  # Para respuestas más rápidas y económicas (default)
```

## 🐛 Solución de Problemas

### OpenAI no funciona

```bash
# Verificar que la API key esté configurada
cat .env | grep OPENAI_API_KEY

# Probar conexión
python -c "from orion_ai import get_orion_ai; ai = get_orion_ai(); print('✓ OK')"
```

### Error "OrionAI no disponible"

1. Verificar que `OPENAI_API_KEY` esté en `.env`
2. Instalar dependencias: `pip install openai python-dotenv`
3. Reiniciar ORION: `python app.py`

## 📊 Costos de API

### OpenAI (GPT-4o-mini)
- Análisis de deudas: ~$0.002 por análisis
- Plan de pagos: ~$0.001 por plan
- Chat: ~$0.0005 por pregunta

**Estimado mensual** (uso moderado): ~$0.50 - $2.00 USD

## 🔒 Seguridad

- ✅ `.env` excluido de git
- ✅ API keys nunca expuestas en código

## 📚 Recursos

- [Documentación OpenAI](https://platform.openai.com/docs)
- [FastAPI Docs](https://fastapi.tiangolo.com)

## 🤝 Contribuir

Para más detalles técnicos, ver `CLAUDE.md` y `ORION_GUIDE.md`.

---

**ORION** - Tu asistente inteligente para proyectos y finanzas
*Desarrollado con FastAPI y OpenAI GPT-4*
