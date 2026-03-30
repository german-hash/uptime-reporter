def build_email_body(mes_nombre: str, anio: int, chart_b64: str = None, uptime_mes: float = None) -> str:
    chart_html = ""
    if chart_b64:
        chart_html = f"""
    <div style="margin: 20px 0;">
      <img src="data:image/png;base64,{chart_b64}"
           alt="Promedio Uptime Mensual"
           style="width:100%; max-width:600px; display:block; border-radius:6px;">
    </div>
"""

    uptime_str = f" · Uptime {uptime_mes:.2f}%" if uptime_mes is not None else ""

    return f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <style>
    body {{ font-family: Arial, sans-serif; font-size: 14px; color: #2d2d2d; line-height: 1.7; }}
    .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
    .header-bar {{ background: #2d2d2d; color: #FFC000; font-size: 13px; font-weight: 700; padding: 10px 16px; border-radius: 6px 6px 0 0; letter-spacing: 0.5px; }}
    .body-box {{ border: 1px solid #e2e5ea; border-top: none; border-radius: 0 0 6px 6px; padding: 20px; background: #ffffff; }}
    .footer {{ margin-top: 24px; color: #888; font-size: 12px; border-top: 1px solid #e2e5ea; padding-top: 16px; }}
  </style>
</head>
<body>
  <div class="container">
    <div class="header-bar">{mes_nombre} {anio}{uptime_str}</div>
    <div class="body-box">
      <p>Buenos días Equipo!</p>
      <br>
      <p>Les dejo el reporte de uptime de nuestro ecosistema digital al mes de <strong>{mes_nombre} {anio}</strong> cerrado.</p>
      <br>
      <p>En el adjunto, encontrarán las explicaciones para el entendimiento de lo que se está midiendo, también un detalle de los eventos ocurridos.</p>

      {chart_html}

      <div class="footer">
        Quedamos a disposición para cualquier consulta o comentario.<br>
        Muchas Gracias · Fuerte abrazo.
      </div>
    </div>
  </div>
</body>
</html>"""