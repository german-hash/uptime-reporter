import io
import base64
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

MESES_ORDER = [
    "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
    "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"
]


def generate_chart_base64(meses_data: dict) -> str:
    values = []
    for i in range(1, 13):
        if i in meses_data:
            values.append(meses_data[i]["promedio"])
        else:
            values.append(None)

    fig, ax = plt.subplots(figsize=(10, 4))
    fig.patch.set_facecolor('#ffffff')
    ax.set_facecolor('#ffffff')

    x = np.arange(len(MESES_ORDER))
    bar_colors = ['#1a56db' if v is not None else '#e2e5ea' for v in values]
    bar_values = [v if v is not None else 0 for v in values]

    bars = ax.bar(x, bar_values, color=bar_colors, width=0.5, zorder=3, bottom=99.2)

    # Adjust bars to start from 99.2 baseline
    for bar, val in zip(bars, bar_values):
        if val > 0:
            bar.set_y(99.2)
            bar.set_height(val - 99.2)

    # Reference lines
    ax.axhline(y=99.90, color='#16a34a', linewidth=1.5, linestyle='--', zorder=4, label='Objetivo 99.90%')
    ax.axhline(y=99.70, color='#dc2626', linewidth=1.5, linestyle='--', zorder=4, label='Mínimo 99.70%')

    # Labels on bars
    for i, val in enumerate(values):
        if val is not None:
            ax.text(i, val + 0.005, f'{val:.2f}', ha='center', va='bottom',
                   fontsize=8, fontweight='bold', color='#1a56db')

    ax.set_xticks(x)
    ax.set_xticklabels(MESES_ORDER, fontsize=8, color='#6b7280')
    ax.set_ylim(99.2, 100.15)
    ax.set_yticks([99.20, 99.40, 99.60, 99.70, 99.80, 99.90, 100.00])
    ax.set_yticklabels([f'{v:.2f}' for v in [99.20, 99.40, 99.60, 99.70, 99.80, 99.90, 100.00]],
                       fontsize=8, color='#6b7280')

    ax.grid(axis='y', color='#e2e5ea', linewidth=0.8, zorder=0)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color('#e2e5ea')
    ax.spines['bottom'].set_color('#e2e5ea')

    ax.set_title('Promedio Uptime Mensual', fontsize=12, fontweight='bold',
                 color='#1a1d23', pad=12)

    legend = ax.legend(fontsize=8, loc='lower right', framealpha=0.9,
                      edgecolor='#e2e5ea')

    plt.tight_layout()

    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=150, bbox_inches='tight',
                facecolor='white', edgecolor='none')
    plt.close(fig)
    buf.seek(0)

    return base64.b64encode(buf.read()).decode('utf-8')


def generate_report_html(data: dict, mes_nombre: str, anio: int) -> str:
    meses_data = data["meses"]
    ytd = data["ytd"]

    # Generate chart as base64 image
    chart_b64 = generate_chart_base64(meses_data)

    # Build event rows
    rows_html = ""
    for mes_num in sorted(meses_data.keys()):
        m = meses_data[mes_num]
        mes_label = m["nombre"].upper()
        rows_html += f"""
        <tr class="month-header">
          <td colspan="9">TOTAL {mes_label} — {m['total_hs']} hs</td>
        </tr>
        """
        for ev in m["eventos"]:
            fecha = ev["fecha"]
            if hasattr(fecha, "strftime"):
                fecha_str = fecha.strftime("%d/%m/%Y")
            else:
                fecha_str = str(fecha)[:10]
            rows_html += f"""
            <tr>
              <td>{fecha_str}</td>
              <td>{ev['descripcion_incidente']}</td>
              <td>{ev['total_hs_mes']}</td>
              <td>{ev['caida_flex_d']}</td>
              <td>{ev['caida_mop_dlp']}</td>
              <td>{ev['caida_cupones']}</td>
              <td>{ev['baja_perf_flex_d']}</td>
              <td>{ev['baja_perf_mop_dlp']}</td>
              <td>{ev['baja_perf_cupones']}</td>
            </tr>
            """
        rows_html += f"""
        <tr class="stats-row">
          <td colspan="2">Promedio Uptime: <strong>{m['promedio']}%</strong></td>
          <td></td>
          <td>{m['uptime_flex']}%</td>
          <td>{m['uptime_mop']}%</td>
          <td>{m['uptime_cup']}%</td>
          <td>{m['perform_flex']}%</td>
          <td>{m['perform_mop']}%</td>
          <td>{m['perform_cup']}%</td>
        </tr>
        """

    html = f"""<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Uptime Ecosistema Digital — {mes_nombre} {anio}</title>
  <link href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600;700&display=swap" rel="stylesheet">
  <style>
    :root {{
      --bg: #f7f8fa;
      --surface: #ffffff;
      --surface2: #f0f2f5;
      --border: #e2e5ea;
      --text: #1a1d23;
      --text-muted: #6b7280;
      --accent: #1a56db;
      --accent-light: #e8effe;
      --green: #16a34a;
      --green-light: #dcfce7;
      --red: #dc2626;
      --red-light: #fee2e2;
      --yellow: #d97706;
      --radius: 10px;
    }}
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{ font-family: 'DM Sans', Arial, sans-serif; background: var(--bg); color: var(--text); font-size: 14px; line-height: 1.5; }}
    .page {{ max-width: 960px; margin: 0 auto; padding: 40px 24px; }}
    .header {{ display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 40px; padding-bottom: 24px; border-bottom: 2px solid var(--border); }}
    .header-left h1 {{ font-size: 26px; font-weight: 700; color: var(--text); letter-spacing: -0.5px; }}
    .header-left .subtitle {{ font-size: 14px; color: var(--text-muted); margin-top: 4px; }}
    .ytd-badge {{ display: inline-block; background: var(--accent); color: white; font-size: 13px; font-weight: 600; padding: 6px 14px; border-radius: 20px; }}
    .ytd-label {{ font-size: 11px; color: var(--text-muted); margin-top: 4px; font-weight: 500; text-transform: uppercase; letter-spacing: 0.5px; text-align: right; }}
    .section {{ background: var(--surface); border: 1px solid var(--border); border-radius: var(--radius); padding: 28px; margin-bottom: 24px; }}
    .section-title {{ font-size: 13px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.8px; color: var(--accent); margin-bottom: 16px; display: flex; align-items: center; gap: 8px; }}
    .section-title::before {{ content: ''; display: block; width: 3px; height: 14px; background: var(--accent); border-radius: 2px; }}
    .context-grid {{ display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 16px; }}
    .context-card {{ background: var(--surface2); border-radius: 8px; padding: 16px; }}
    .context-card h4 {{ font-size: 12px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px; color: var(--accent); margin-bottom: 8px; }}
    .context-card p {{ font-size: 13px; color: var(--text-muted); line-height: 1.5; }}
    .tag {{ display: inline-block; background: var(--accent-light); color: var(--accent); font-size: 11px; font-weight: 600; padding: 2px 8px; border-radius: 4px; margin: 2px 2px 2px 0; }}
    .tag.red {{ background: var(--red-light); color: var(--red); }}
    .chart-img {{ width: 100%; border-radius: 8px; }}
    .table-scroll {{ overflow-x: auto; }}
    table {{ width: 100%; border-collapse: collapse; font-size: 13px; }}
    thead th {{ background: var(--surface2); padding: 10px 12px; text-align: center; font-weight: 600; font-size: 11px; text-transform: uppercase; letter-spacing: 0.5px; color: var(--text-muted); border-bottom: 2px solid var(--border); }}
    thead th.left {{ text-align: left; }}
    tbody td {{ padding: 9px 12px; border-bottom: 1px solid var(--border); text-align: center; color: var(--text); }}
    tbody td:first-child, tbody td:nth-child(2) {{ text-align: left; }}
    tbody tr:hover td {{ background: var(--surface2); }}
    tr.month-header td {{ background: var(--accent); color: white; font-weight: 600; font-size: 12px; text-transform: uppercase; letter-spacing: 0.5px; padding: 8px 12px; text-align: left; }}
    tr.stats-row td {{ background: #f8faff; font-size: 12px; color: var(--text-muted); border-bottom: 1px solid var(--border); }}
    tr.stats-row td strong {{ color: var(--accent); }}
    .comm-table {{ width: 100%; border-collapse: collapse; font-size: 12px; }}
    .comm-table th {{ background: var(--text); color: white; padding: 8px 12px; text-align: left; font-weight: 600; font-size: 11px; text-transform: uppercase; letter-spacing: 0.5px; }}
    .comm-table td {{ padding: 8px 12px; border-bottom: 1px solid var(--border); vertical-align: top; }}
    .comm-table tr.caida td {{ background: #fff7f7; }}
    .comm-table tr.degradacion td {{ background: #fffbf0; }}
    .comm-table tr.resolucion td {{ background: #f0fff4; }}
    .event-badge {{ display: inline-block; padding: 2px 8px; border-radius: 4px; font-weight: 600; font-size: 11px; }}
    .event-badge.caida {{ background: var(--red-light); color: var(--red); }}
    .event-badge.degradacion {{ background: #fef3c7; color: var(--yellow); }}
    .event-badge.resolucion {{ background: var(--green-light); color: var(--green); }}
    .footer {{ text-align: center; margin-top: 40px; padding-top: 20px; border-top: 1px solid var(--border); font-size: 12px; color: var(--text-muted); }}
  </style>
</head>
<body>
<div class="page">

  <div class="header">
    <div class="header-left">
      <h1>Uptime · Ecosistema Digital</h1>
      <div class="subtitle">{mes_nombre} {anio} — Reporte Mensual</div>
    </div>
    <div class="header-right">
      <div class="ytd-badge">YTD {ytd}%</div>
      <div class="ytd-label">Promedio acumulado</div>
    </div>
  </div>

  <div class="section">
    <div class="section-title">Contexto</div>
    <div class="context-grid">
      <div class="context-card">
        <h4>Arcos eCommerce</h4>
        <p><span class="tag">MOP / DLP</span> <span class="tag">Cupones</span></p>
        <p style="margin-top:8px">App · Web · WhatsApp. Componentes independientes.</p>
      </div>
      <div class="context-card">
        <h4>Flex Digital</h4>
        <p>Motor de ventas y operación en restaurante.</p>
        <p style="margin-top:8px"><span class="tag">Motor de Ventas</span></p>
      </div>
      <div class="context-card">
        <h4>Tipos de Evento</h4>
        <span class="tag red">Caída</span> Solución offline.<br><br>
        <span class="tag">Baja de Performance</span> Opera con dificultades.
      </div>
    </div>
  </div>

  <div class="section">
    <div class="section-title">Promedio Uptime Mensual</div>
    <img src="data:image/png;base64,{chart_b64}" class="chart-img" alt="Gráfico Uptime Mensual">
  </div>

  <div class="section">
    <div class="section-title">Detalle de Eventos</div>
    <div class="table-scroll">
      <table>
        <thead>
          <tr>
            <th class="left">Fecha</th>
            <th class="left">Descripción</th>
            <th>Hs Mes</th>
            <th colspan="3">Caída (hs)</th>
            <th colspan="3">Baja Perf. (hs)</th>
          </tr>
          <tr>
            <th></th><th></th><th></th>
            <th>Flex D</th><th>MOP/DLP</th><th>Cupones</th>
            <th>Flex D</th><th>MOP/DLP</th><th>Cupones</th>
          </tr>
        </thead>
        <tbody>
          {rows_html}
        </tbody>
      </table>
    </div>
  </div>

  <div class="section">
    <div class="section-title">Esquema de Comunicación</div>
    <table class="comm-table">
      <thead>
        <tr><th>Evento</th><th>Scope</th><th>Momento</th><th>Audiencia</th><th>Responsable</th><th>Para qué</th></tr>
      </thead>
      <tbody>
        <tr class="caida"><td rowspan="4"><span class="event-badge caida">Caída</span></td><td rowspan="4">Ecosistema completo o componentes únicos</td><td>En la detección</td><td>Equipos de IT</td><td>PO / Quien detecta</td><td>Dimensionar impacto y workarounds</td></tr>
        <tr class="caida"><td>A los 10'</td><td>Liderazgo CTO / Call Center</td><td>Germán / Mónica / Diego</td><td>Puesta en conocimiento e impactos</td></tr>
        <tr class="caida"><td>A los 30'</td><td>MD's IT Div / IT País</td><td>IT Div / IT País</td><td>Acciones particulares</td></tr>
        <tr class="caida"><td>A los 60'</td><td>Management Board</td><td>—</td><td>Puesta en conocimiento</td></tr>
        <tr class="degradacion"><td rowspan="3"><span class="event-badge degradacion">Degradación</span></td><td rowspan="3">Componentes</td><td>En la detección</td><td>Equipos de IT</td><td>PO / Quien detecta</td><td>Dimensionar impacto y workarounds</td></tr>
        <tr class="degradacion"><td>A los 15'</td><td>Liderazgo CTO / Call Center</td><td>Germán / Mónica / Diego</td><td>Comentar componente e impacto</td></tr>
        <tr class="degradacion"><td>A los 60'</td><td>MD's IT Div / IT País</td><td>IT Div / IT País</td><td>Acciones particulares</td></tr>
        <tr class="resolucion"><td><span class="event-badge resolucion">Resolución</span></td><td>Componente afectado</td><td>Al confirmar resolución</td><td>IT / Advance / Mercado</td><td>Germán / Mónica / Diego</td><td>Informar tiempo afectado y GO del servicio</td></tr>
      </tbody>
    </table>
  </div>

  <div class="footer">Generado automáticamente · {mes_nombre} {anio} · Ecosistema Digital</div>

</div>
</body>
</html>"""
    return html
