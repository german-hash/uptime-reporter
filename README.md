# Uptime Reporter — Setup Guide

## Estructura del proyecto

```
uptime-reporter/
├── main.py              # FastAPI app — endpoint principal
├── report_generator.py  # Genera el HTML del reporte
├── email_templates.py   # Cuerpo del mail
├── requirements.txt     # Dependencias
├── render.yaml          # Config de deploy en Render
└── README.md
```

---

## Variables de entorno (configurar en Render)

| Variable | Descripción |
|---|---|
| `API_KEY` | Clave secreta para autenticar requests desde Make |
| `GMAIL_USER` | Tu cuenta Gmail (ej: tumail@gmail.com) |
| `GMAIL_APP_PASSWORD` | App Password de Gmail (no tu contraseña normal) |
| `GOOGLE_SERVICE_ACCOUNT_JSON` | JSON completo de la Service Account de Google |
| `DRIVE_FILE_ID` | ID del archivo `Uptime_Events.xlsx` en Google Drive |
| `RECIPIENTS` | Emails separados por coma (ej: a@x.com,b@x.com) |

---

## Setup Gmail App Password

1. Ir a https://myaccount.google.com/security
2. Activar verificación en dos pasos
3. Buscar "Contraseñas de aplicaciones"
4. Crear una nueva → copiar los 16 caracteres
5. Pegar en `GMAIL_APP_PASSWORD`

---

## Setup Google Drive (Service Account)

1. Ir a https://console.cloud.google.com
2. Crear proyecto (o usar uno existente)
3. Habilitar **Google Drive API**
4. Ir a "Credenciales" → Crear credencial → **Cuenta de servicio**
5. Descargar el JSON de la cuenta de servicio
6. Pegar el contenido completo del JSON en `GOOGLE_SERVICE_ACCOUNT_JSON`
7. Compartir el archivo `Uptime_Events.xlsx` en Drive con el email de la service account (tiene la forma `xxx@xxx.iam.gserviceaccount.com`)
8. El `DRIVE_FILE_ID` es la parte de la URL de Drive: `https://drive.google.com/file/d/ESTE_ES_EL_ID/view`

---

## Deploy en Render

1. Crear repo en GitHub con estos archivos
2. En Render → New Web Service → conectar repo
3. Configurar las variables de entorno
4. Deploy

El endpoint quedará en: `https://tu-app.onrender.com/send-report`

---

## Configuración en Make

### Escenario
- **Trigger**: Schedule (1° día hábil de cada mes, o manual)
- **Módulo**: HTTP → Make a request

### Configuración del módulo HTTP
- **URL**: `https://tu-app.onrender.com/send-report`
- **Method**: POST
- **Headers**:
  - `x-api-key`: tu API_KEY
  - `Content-Type`: application/json
- **Body** (JSON, opcional — para forzar mes):
```json
{
  "mes_nombre": "Marzo",
  "anio": 2026
}
```
Si no mandás body, el script infiere el último mes disponible en el Excel.

---

## Estructura del Excel (Uptime_Events.xlsx)

Sheet: `Eventos`

| Columna | Descripción |
|---|---|
| `fecha` | Fecha del evento |
| `descripcion_incidente` | Descripción libre |
| `total_hs_mes` | Total de horas del mes (ej: 744 para enero) |
| `caida_flex_d` | Horas de caída Flex Digital |
| `caida_mop_dlp` | Horas de caída MOP/DLP |
| `caida_cupones` | Horas de caída Cupones |
| `baja_perf_flex_d` | Horas de baja performance Flex Digital |
| `baja_perf_mop_dlp` | Horas de baja performance MOP/DLP |
| `baja_perf_cupones` | Horas de baja performance Cupones |

Agregar una fila por evento. Si no hubo incidentes en el mes, agregar igual una fila con `sin incidentes` y todos los valores en 0.

---

## Test local

```bash
pip install -r requirements.txt
uvicorn main:app --reload
```

Luego POST a `http://localhost:8000/send-report` con header `x-api-key: changeme`.
