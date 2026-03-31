import os
import io
import base64
import pandas as pd
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime
import requests
from fastapi import FastAPI, HTTPException, Header
from pydantic import BaseModel
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from report_generator import generate_report_html, generate_chart_base64
from email_templates import build_email_body

app = FastAPI(title="Uptime Reporter")

API_KEY = os.environ.get("API_KEY", "changeme")
GMAIL_USER = os.environ.get("GMAIL_USER")
RESEND_API_KEY = os.environ.get("RESEND_API_KEY")
GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET")
GOOGLE_REFRESH_TOKEN = os.environ.get("GOOGLE_REFRESH_TOKEN")
DRIVE_FILE_ID = os.environ.get("DRIVE_FILE_ID")
RECIPIENTS = os.environ.get("RECIPIENTS", "").split(",")


def get_google_creds():
    creds = Credentials(
        token=None,
        refresh_token=GOOGLE_REFRESH_TOKEN,
        token_uri="https://oauth2.googleapis.com/token",
        client_id=GOOGLE_CLIENT_ID,
        client_secret=GOOGLE_CLIENT_SECRET,
    )
    creds.refresh(Request())
    return creds


class TriggerRequest(BaseModel):
    mes_nombre: str = None
    anio: int = None


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/send-report")
def send_report(
    body: TriggerRequest = TriggerRequest(),
    x_api_key: str = Header(None)
):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized")

    try:
        excel_bytes = download_from_drive(DRIVE_FILE_ID)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error descargando Drive: {e}")

    try:
        data = parse_uptime_excel(excel_bytes)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error parseando Excel: {e}")

    mes_nombre = body.mes_nombre or data["ultimo_mes"]
    anio = body.anio or datetime.now().year

    html_report = generate_report_html(data, mes_nombre, anio)
    chart_b64 = generate_chart_base64(data["meses"], ytd=data["ytd"])
    ultimo_mes_num = max(data["meses"].keys()) if data["meses"] else None
    uptime_mes = data["meses"][ultimo_mes_num]["promedio"] if ultimo_mes_num else None
    email_body_html = build_email_body(mes_nombre, anio, chart_b64, uptime_mes)

    try:
        send_email_resend(
            subject=f"Reporte Uptime Ecosistema Digital - {mes_nombre} {anio}",
            body_html=email_body_html,
            attachment_html=html_report,
            attachment_name=f"Uptime_{mes_nombre}_{anio}.html",
            recipients=RECIPIENTS,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error enviando mail: {e}")

    return {"status": "ok", "mes": mes_nombre, "anio": anio, "recipients": RECIPIENTS}


def download_from_drive(file_id: str) -> bytes:
    creds = get_google_creds()
    service = build("drive", "v3", credentials=creds)
    request = service.files().get_media(fileId=file_id)
    buf = io.BytesIO()
    downloader = MediaIoBaseDownload(buf, request)
    done = False
    while not done:
        _, done = downloader.next_chunk()
    return buf.getvalue()


def parse_uptime_excel(excel_bytes: bytes) -> dict:
    df = pd.read_excel(io.BytesIO(excel_bytes), sheet_name="Eventos")

    meses_esp = {
        1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril",
        5: "Mayo", 6: "Junio", 7: "Julio", 8: "Agosto",
        9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre"
    }

    df["fecha"] = pd.to_datetime(df["fecha"])
    df["mes_num"] = df["fecha"].dt.month

    meses_data = {}
    for mes_num, group in df.groupby("mes_num"):
        total_hs = group["total_hs_mes"].iloc[0]
        caida_flex = group["caida_flex_d"].sum()
        caida_mop = group["caida_mop_dlp"].sum()
        caida_cup = group["caida_cupones"].sum()
        perf_flex = group["baja_perf_flex_d"].sum()
        perf_mop = group["baja_perf_mop_dlp"].sum()
        perf_cup = group["baja_perf_cupones"].sum()

        uptime_flex = round(100 - (caida_flex * 100 / total_hs), 2) if total_hs else 100
        uptime_mop = round(100 - (caida_mop * 100 / total_hs), 2) if total_hs else 100
        uptime_cup = round(100 - (caida_cup * 100 / total_hs), 2) if total_hs else 100
        perform_flex = round(100 - (perf_flex * 100 / total_hs), 2) if total_hs else 100
        perform_mop = round(100 - (perf_mop * 100 / total_hs), 2) if total_hs else 100
        perform_cup = round(100 - (perf_cup * 100 / total_hs), 2) if total_hs else 100
        promedio = round((uptime_flex + uptime_mop + uptime_cup + perform_flex + perform_mop + perform_cup) / 6, 2)

        eventos = group[["fecha", "descripcion_incidente", "total_hs_mes",
                          "caida_flex_d", "caida_mop_dlp", "caida_cupones",
                          "baja_perf_flex_d", "baja_perf_mop_dlp", "baja_perf_cupones"]].to_dict("records")

        meses_data[mes_num] = {
            "nombre": meses_esp[mes_num],
            "total_hs": total_hs,
            "uptime_flex": uptime_flex,
            "uptime_mop": uptime_mop,
            "uptime_cup": uptime_cup,
            "perform_flex": perform_flex,
            "perform_mop": perform_mop,
            "perform_cup": perform_cup,
            "promedio": promedio,
            "eventos": eventos,
        }

    promedios = [v["promedio"] for v in meses_data.values()]
    ytd = round(sum(promedios) / len(promedios), 2) if promedios else 0
    ultimo_mes = meses_esp[max(meses_data.keys())] if meses_data else "—"

    return {
        "meses": meses_data,
        "ytd": ytd,
        "ultimo_mes": ultimo_mes,
        "meses_esp": meses_esp,
    }


def send_email_resend(subject, body_html, attachment_html, attachment_name, recipients):
    attachment_b64 = base64.b64encode(attachment_html.encode("utf-8")).decode("utf-8")

    payload = {
        "from": f"Uptime Reporter <onboarding@resend.dev>",
        "to": recipients,
        "subject": subject,
        "html": body_html,
        "attachments": [
            {
                "filename": attachment_name,
                "content": attachment_b64,
            }
        ]
    }

    response = requests.post(
        "https://api.resend.com/emails",
        headers={
            "Authorization": f"Bearer {RESEND_API_KEY}",
            "Content-Type": "application/json"
        },
        json=payload
    )

    if response.status_code not in (200, 201):
        raise Exception(f"Resend error {response.status_code}: {response.text}")