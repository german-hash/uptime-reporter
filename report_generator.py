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

# Colores corporativos
GOLD = "#FFC000"
DARK = "#2d2d2d"
GRAY = "#4a4a4a"
LIGHT_GOLD = "#FFF3CC"
RED = "#C00000"
GREEN = "#375623"


def generate_chart_base64(meses_data: dict, ytd: float = None, ultimo_mes_nombre: str = None, ultimo_mes_promedio: float = None) -> str:
    values = []
    for i in range(1, 13):
        if i in meses_data:
            values.append(meses_data[i]["promedio"])
        else:
            values.append(None)

    fig, ax = plt.subplots(figsize=(10, 4.2))
    fig.patch.set_facecolor('#ffffff')
    ax.set_facecolor('#ffffff')

    x = np.arange(len(MESES_ORDER))
    bar_colors = [GOLD if v is not None else '#e2e5ea' for v in values]
    bar_values = [v if v is not None else 99.2 for v in values]

    for i, (val, color) in enumerate(zip(bar_values, bar_colors)):
        if values[i] is not None:
            ax.bar(i, val - 99.2, bottom=99.2, color=color, width=0.5, zorder=3)
            ax.text(i, val + 0.005, f'{val:.2f}', ha='center', va='bottom',
                   fontsize=8, fontweight='bold', color=DARK)

    ax.axhline(y=99.90, color=GREEN, linewidth=1.5, linestyle='--', zorder=4, label='Objetivo 99.90%')
    ax.axhline(y=99.70, color=RED, linewidth=1.5, linestyle='--', zorder=4, label='Mínimo 99.70%')

    ax.set_xticks(x)
    ax.set_xticklabels(MESES_ORDER, fontsize=8, color=GRAY)
    ax.set_ylim(99.2, 100.2)
    ax.set_yticks([99.20, 99.40, 99.60, 99.70, 99.80, 99.90, 100.00])
    ax.set_yticklabels([f'{v:.2f}' for v in [99.20, 99.40, 99.60, 99.70, 99.80, 99.90, 100.00]],
                       fontsize=8, color=GRAY)

    ax.grid(axis='y', color='#e2e5ea', linewidth=0.8, zorder=0)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color('#e2e5ea')
    ax.spines['bottom'].set_color('#e2e5ea')
    ax.set_title('Promedio Uptime Mensual', fontsize=12, fontweight='bold', color=DARK, pad=12)
    ax.legend(fontsize=8, loc='lower right', framealpha=0.9, edgecolor='#e2e5ea')

    # YTD box — bottom right inside chart
    if ytd is not None:
        box_text = f"PROMEDIO YTD    {ytd:.2f}"
        ax.text(0.98, 0.04, box_text, transform=ax.transAxes,
                fontsize=10, fontweight='bold', color=DARK,
                ha='right', va='bottom',
                bbox=dict(boxstyle='round,pad=0.5', facecolor='white',
                          edgecolor=DARK, linewidth=1.5))

    plt.tight_layout()
    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=150, bbox_inches='tight', facecolor='white', edgecolor='none')
    plt.close(fig)
    buf.seek(0)
    return base64.b64encode(buf.read()).decode('utf-8')


def generate_report_html(data: dict, mes_nombre: str, anio: int) -> str:
    meses_data = data["meses"]
    ytd = data["ytd"]

    # Last month promedio
    ultimo_mes_num = max(meses_data.keys()) if meses_data else None
    ultimo_mes_promedio = meses_data[ultimo_mes_num]["promedio"] if ultimo_mes_num else None

    chart_b64 = generate_chart_base64(meses_data, ytd=ytd)

    # Build trimestre groupings
    trimestres = {
        "Q1": [1, 2, 3],
        "Q2": [4, 5, 6],
        "Q3": [7, 8, 9],
        "Q4": [10, 11, 12],
    }

    rows_html = ""
    for q_name, q_meses in trimestres.items():
        q_has_data = any(m in meses_data for m in q_meses)
        for mes_num in q_meses:
            if mes_num not in meses_data:
                continue
            m = meses_data[mes_num]
            mes_label = m["nombre"].upper()

            # Month header row
            rows_html += f"""
            <tr class="month-header">
              <td>TOTAL {mes_label}</td>
              <td>{m['total_hs']}</td>
              <td class="caida-col"></td><td class="caida-col"></td><td class="caida-col"></td>
              <td class="perf-col"></td><td class="perf-col"></td><td class="perf-col"></td>
              <td class="stats-col">{m['uptime_flex']}%</td>
              <td class="stats-col">{m['uptime_mop']}%</td>
              <td class="stats-col">{m['uptime_cup']}%</td>
              <td class="stats-col">{m['perform_flex']}%</td>
              <td class="stats-col">{m['perform_mop']}%</td>
              <td class="stats-col">{m['perform_cup']}%</td>
              <td class="promedio-col">{m['promedio']}%</td>
            </tr>
            """
            # Event rows
            for ev in m["eventos"]:
                fecha = ev["fecha"]
                fecha_str = fecha.strftime("%d/%m/%Y") if hasattr(fecha, "strftime") else str(fecha)[:10]
                rows_html += f"""
                <tr class="event-row">
                  <td colspan="1" style="padding-left:24px; font-size:12px; color:#555;">{fecha_str} — {ev['descripcion_incidente']}</td>
                  <td style="font-size:12px;">{ev['total_hs_mes']}</td>
                  <td class="caida-col">{ev['caida_flex_d'] or ''}</td>
                  <td class="caida-col">{ev['caida_mop_dlp'] or ''}</td>
                  <td class="caida-col">{ev['caida_cupones'] or ''}</td>
                  <td class="perf-col">{ev['baja_perf_flex_d'] or ''}</td>
                  <td class="perf-col">{ev['baja_perf_mop_dlp'] or ''}</td>
                  <td class="perf-col">{ev['baja_perf_cupones'] or ''}</td>
                  <td class="stats-col"></td><td class="stats-col"></td><td class="stats-col"></td>
                  <td class="stats-col"></td><td class="stats-col"></td><td class="stats-col"></td>
                  <td class="promedio-col"></td>
                </tr>
                """

        # Trimestre total row
        if q_has_data:
            q_data = [meses_data[m] for m in q_meses if m in meses_data]
            q_promedio = round(sum(m["promedio"] for m in q_data) / len(q_data), 2) if q_data else 0
            rows_html += f"""
            <tr class="quarter-row">
              <td>TOTAL {q_name}</td>
              <td></td>
              <td class="caida-col"></td><td class="caida-col"></td><td class="caida-col"></td>
              <td class="perf-col"></td><td class="perf-col"></td><td class="perf-col"></td>
              <td class="stats-col"></td><td class="stats-col"></td><td class="stats-col"></td>
              <td class="stats-col"></td><td class="stats-col"></td><td class="stats-col"></td>
              <td class="promedio-col">{q_promedio}%</td>
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
      --gold: #FFC000;
      --gold-light: #FFF3CC;
      --gold-mid: #FFD966;
      --dark: #2d2d2d;
      --gray: #4a4a4a;
      --border: #e2e5ea;
      --surface: #ffffff;
      --bg: #f5f5f5;
      --red: #C00000;
      --green: #375623;
      --caida-bg: #FFCCCC;
      --perf-bg: #FFEB9C;
      --stats-bg: #DDEBF7;
      --promedio-bg: #E2EFDA;
    }}
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{ font-family: 'DM Sans', Arial, sans-serif; background: var(--bg); color: var(--dark); font-size: 14px; line-height: 1.5; }}
    .page {{ max-width: 1100px; margin: 0 auto; padding: 32px 24px; }}

    /* HEADER */
    .header {{ background: var(--dark); color: white; border-radius: 10px 10px 0 0; padding: 24px 28px; display: flex; justify-content: space-between; align-items: center; margin-bottom: 0; }}
    .header h1 {{ font-size: 22px; font-weight: 700; letter-spacing: -0.3px; }}
    .header .subtitle {{ font-size: 13px; color: var(--gold); margin-top: 4px; font-weight: 500; }}
    .ytd-badge {{ background: var(--gold); color: var(--dark); font-size: 14px; font-weight: 700; padding: 8px 18px; border-radius: 20px; }}
    .ytd-label {{ font-size: 11px; color: #aaa; margin-top: 4px; text-align: right; text-transform: uppercase; letter-spacing: 0.5px; }}

    /* SECTIONS */
    .section {{ background: var(--surface); border: 1px solid var(--border); padding: 24px 28px; margin-bottom: 20px; }}
    .section:first-of-type {{ border-radius: 0; }}
    .section {{ border-radius: 0 0 10px 10px; }}
    .section + .section {{ border-radius: 10px; }}
    .section-title {{ font-size: 11px; font-weight: 700; text-transform: uppercase; letter-spacing: 1px; color: var(--gray); margin-bottom: 16px; padding-bottom: 8px; border-bottom: 2px solid var(--gold); display: inline-block; }}

    /* CONTEXT */
    .context-grid {{ display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 14px; }}
    .context-card {{ background: var(--gold-light); border-radius: 8px; padding: 14px; border-left: 3px solid var(--gold); }}
    .context-card h4 {{ font-size: 11px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px; color: var(--dark); margin-bottom: 8px; }}
    .context-card p {{ font-size: 12px; color: var(--gray); line-height: 1.5; }}
    .tag {{ display: inline-block; background: var(--gold); color: var(--dark); font-size: 10px; font-weight: 700; padding: 2px 7px; border-radius: 3px; margin: 2px 2px 2px 0; }}
    .tag.red {{ background: var(--caida-bg); color: var(--red); }}

    /* CHART */
    .chart-img {{ width: 100%; border-radius: 6px; }}

    /* TABLE */
    .table-scroll {{ overflow-x: auto; }}
    table {{ width: 100%; border-collapse: collapse; font-size: 12px; }}

    /* Header rows */
    .col-group th {{ padding: 6px 8px; text-align: center; font-weight: 700; font-size: 11px; color: white; }}
    .col-group .th-caida {{ background: var(--red); }}
    .col-group .th-perf {{ background: #FF8C00; }}
    .col-group .th-stats {{ background: #2E75B6; }}
    .col-group .th-main {{ background: var(--dark); }}
    .col-group .th-promedio {{ background: var(--green); }}

    .col-sub th {{ background: #f0f0f0; padding: 6px 8px; text-align: center; font-weight: 600; font-size: 10px; color: var(--gray); border-bottom: 2px solid var(--border); }}
    .col-sub th.left {{ text-align: left; }}

    /* Data rows */
    tbody td {{ padding: 7px 8px; border-bottom: 1px solid var(--border); text-align: center; }}
    tbody td:first-child {{ text-align: left; }}
    .caida-col {{ background: #FFF0F0; }}
    .perf-col {{ background: #FFFBF0; }}
    .stats-col {{ background: #F0F6FF; }}
    .promedio-col {{ background: #F0FFF0; font-weight: 700; color: var(--green); }}

    tr.month-header td {{ background: var(--gold); color: var(--dark); font-weight: 700; font-size: 11px; text-transform: uppercase; padding: 7px 8px; }}
    tr.month-header .caida-col {{ background: #FFD966; }}
    tr.month-header .perf-col {{ background: #FFD966; }}
    tr.month-header .stats-col {{ background: #FFD966; }}
    tr.month-header .promedio-col {{ background: #E8B400; font-weight: 700; }}

    tr.event-row td {{ background: white; font-size: 12px; }}
    tr.event-row .caida-col {{ background: #FFF0F0; }}
    tr.event-row .perf-col {{ background: #FFFBF0; }}
    tr.event-row .stats-col {{ background: #F0F6FF; }}
    tr.event-row .promedio-col {{ background: #F0FFF0; }}

    tr.quarter-row td {{ background: var(--dark); color: white; font-weight: 700; font-size: 11px; padding: 7px 8px; text-align: center; }}
    tr.quarter-row td:first-child {{ text-align: left; }}
    tr.quarter-row .promedio-col {{ background: #1a4a1a; color: #90EE90; }}

    /* COMM TABLE */
    .comm-table {{ width: 100%; border-collapse: collapse; font-size: 12px; }}
    .comm-table th {{ background: var(--dark); color: white; padding: 8px 12px; text-align: left; font-weight: 600; font-size: 11px; text-transform: uppercase; letter-spacing: 0.5px; }}
    .comm-table td {{ padding: 8px 12px; border-bottom: 1px solid var(--border); vertical-align: top; }}
    .comm-table tr.caida td {{ background: #FFF0F0; }}
    .comm-table tr.degradacion td {{ background: #FFFBF0; }}
    .comm-table tr.resolucion td {{ background: #F0FFF4; }}
    .event-badge {{ display: inline-block; padding: 2px 8px; border-radius: 4px; font-weight: 600; font-size: 11px; }}
    .event-badge.caida {{ background: #FFCCCC; color: var(--red); }}
    .event-badge.degradacion {{ background: #FFEB9C; color: #7a5000; }}
    .event-badge.resolucion {{ background: #CCFFCC; color: var(--green); }}

    .footer {{ text-align: center; margin-top: 32px; padding-top: 16px; border-top: 1px solid var(--border); font-size: 11px; color: #999; }}
  </style>
</head>
<body>
<div class="page">

  <!-- HEADER -->
  <div class="header">
    <div>
      <div class="subtitle">#TodosSomosDigitales</div>
      <h1>Uptime · Ecosistema Digital</h1>
      <div style="font-size:13px; color:#ccc; margin-top:4px;">{mes_nombre} {anio} — Reporte Mensual</div>
    </div>
    <div style="text-align:right;">
      <div class="ytd-badge">YTD {ytd}%</div>
      <div class="ytd-label">Promedio acumulado</div>
    </div>
  </div>

  <!-- CONTEXTO -->
  <div class="section" style="border-radius:0; border-top:none;">
    <div class="section-title">Contexto</div>
    <div class="context-grid">
      <div class="context-card">
        <h4>Arcos eCommerce</h4>
        <p><span class="tag">MOP / DLP</span> <span class="tag">Cupones</span></p>
        <p style="margin-top:8px">App · Web · WhatsApp. Componentes independientes — si uno está offline, el otro puede operar.</p>
      </div>
      <div class="context-card">
        <h4>Flex Digital</h4>
        <p>Motor de ventas y operación en restaurante.</p>
        <p style="margin-top:8px"><span class="tag">Motor de Ventas</span></p>
      </div>
      <div class="context-card">
        <h4>Tipos de Evento</h4>
        <p><span class="tag red">Caída</span> Solución offline, no puede operar.</p>
        <p style="margin-top:6px;"><span class="tag">Baja de Performance</span> Opera lento y/o con dificultades.</p>
      </div>
    </div>
  </div>

  <!-- GRÁFICO -->
  <div class="section">
    <div class="section-title">Promedio Uptime Mensual</div>
    <img src="data:image/png;base64,{chart_b64}" class="chart-img" alt="Gráfico Uptime Mensual">
  </div>

  <!-- TABLA -->
  <div class="section">
    <div class="section-title">Detalle de Eventos y Estadísticas</div>
    <div class="table-scroll">
      <table>
        <thead>
          <tr class="col-group">
            <th class="th-main left" style="text-align:left;">Descripción del Incidente</th>
            <th class="th-main">Total Hs Mes</th>
            <th class="th-caida" colspan="3">Caída</th>
            <th class="th-perf" colspan="3">Baja de Performance</th>
            <th class="th-stats" colspan="3">Uptime</th>
            <th class="th-stats" colspan="3">Performance</th>
            <th class="th-promedio">Promedio Uptime</th>
          </tr>
          <tr class="col-sub">
            <th class="left"></th>
            <th></th>
            <th>Flex D</th><th>MOP/DLP</th><th>Cupones</th>
            <th>Flex D</th><th>MOP/DLP</th><th>Cupones</th>
            <th>Flex D</th><th>MOP/DLP</th><th>Cupones</th>
            <th>Flex D</th><th>MOP/DLP</th><th>Cupones</th>
            <th></th>
          </tr>
        </thead>
        <tbody>
          {rows_html}
        </tbody>
      </table>
    </div>
  </div>

  <!-- ESQUEMA DE COMUNICACIÓN -->
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

  <div class="footer">Generado automáticamente · {mes_nombre} {anio} · Ecosistema Digital · #TodosSomosDigitales</div>

</div>
</body>
</html>"""
    return html