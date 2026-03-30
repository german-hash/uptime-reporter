def build_email_body(mes_nombre: str, anio: int, chart_b64: str = None) -> str:
    chart_html = ""
    if chart_b64:
        chart_html = f"""
    <div style="margin: 24px 0;">
      <img src="data:image/png;base64,{chart_b64}" 
           alt="Promedio Uptime Mensual" 
           style="width:100%; max-width:600px; display:block; border-radius:8px;">
    </div>
"""
 
    return f"""
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <style>
    body {{ font-family: Arial, sans-serif; font-size: 14px; color: #222; line-height: 1.6; }}
    .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
    .footer {{ margin-top: 30px; color: #555; font-size: 13px; }}
  </style>
</head>
<body>
  <div class="container">
    <p>Buenos días Equipo!</p>
 
    <p>Les dejo el reporte de uptime de nuestro ecosistema digital al mes de <strong>{mes_nombre} {anio}</strong> cerrado.</p>
 
    <p>En el adjunto, encontrarán las explicaciones para el entendimiento de lo que se está midiendo, también un detalle de los eventos ocurridos.</p>
 
    {chart_html}
 
    <div class="footer">
      <p>Quedamos a disposición para cualquier consulta o comentario.<br>
      Muchas Gracias<br>
      Fuerte abrazo.</p>
    </div>
  </div>
</body>
</html>
"""