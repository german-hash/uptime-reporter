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

GOLD = "#FFC000"
DARK = "#2d2d2d"
GRAY = "#888888"
RED = "#C00000"
GREEN = "#375623"


def generate_email_chart_base64(meses_data: dict, ytd: float = None) -> str:
    values = []
    for i in range(1, 13):
        if i in meses_data:
            values.append(meses_data[i]["promedio"])
        else:
            values.append(None)

    fig = plt.figure(figsize=(12, 5.5))
    fig.patch.set_facecolor('#ffffff')

    # Title area above the chart
    fig.text(0.08, 0.95, 'PROMEDIO UPTIME MENSUAL', fontsize=12, fontweight='bold',
             color=DARK, va='top', ha='left', transform=fig.transFigure)

    # Gold underline for title
    from matplotlib.lines import Line2D
    line = Line2D([0.08, 0.22], [0.915, 0.915], transform=fig.transFigure,
                  color=GOLD, linewidth=2)
    fig.add_artist(line)

    ax = fig.add_axes([0.08, 0.08, 0.88, 0.80])
    ax.set_facecolor('#ffffff')

    x = np.arange(len(MESES_ORDER))

    # Bars — wide, from baseline
    for i, val in enumerate(values):
        if val is not None:
            ax.bar(i, val - 99.2, bottom=99.2, color=GOLD, width=0.7, zorder=3)
            ax.text(i, val + 0.008, f'{val:.2f}', ha='center', va='bottom',
                   fontsize=8.5, fontweight='bold', color=DARK)

    # Reference lines
    ax.axhline(y=99.90, color=GREEN, linewidth=1.8, linestyle='--', zorder=4)
    ax.axhline(y=99.70, color=RED, linewidth=1.8, linestyle='--', zorder=4)

    # Legend — top left inside axes
    green_patch = mpatches.Patch(color='none', label='Objetivo 99.90%')
    red_patch = mpatches.Patch(color='none', label='Mínimo 99.70%')
    green_line = plt.Line2D([0], [0], color=GREEN, linewidth=2, linestyle='--', label='Objetivo 99.90%')
    red_line = plt.Line2D([0], [0], color=RED, linewidth=2, linestyle='--', label='Mínimo 99.70%')
    ax.legend(handles=[green_line, red_line], fontsize=8.5, loc='upper left',
              frameon=True, framealpha=0.95, edgecolor='#cccccc',
              bbox_to_anchor=(0.0, 0.98), borderpad=0.8)

    # YTD box — top right
    if ytd is not None:
        ax.text(0.98, 0.97, f"PROMEDIO YTD    {ytd:.2f}", transform=ax.transAxes,
                fontsize=11, fontweight='bold', color=DARK, ha='right', va='top',
                bbox=dict(boxstyle='round,pad=0.5', facecolor='white',
                          edgecolor=DARK, linewidth=2))

    # Axes formatting
    ax.set_xticks(x)
    ax.set_xticklabels(MESES_ORDER, fontsize=8.5, color=GRAY)
    ax.set_ylim(99.2, 100.18)
    ax.set_yticks([99.20, 99.30, 99.40, 99.50, 99.60, 99.70, 99.80, 99.90, 100.00])
    ax.set_yticklabels([f'{v:.2f}' for v in [99.20, 99.30, 99.40, 99.50, 99.60, 99.70, 99.80, 99.90, 100.00]],
                       fontsize=8, color=GRAY)
    ax.grid(axis='y', color='#e8e8e8', linewidth=0.8, zorder=0)
    ax.set_axisbelow(True)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color('#dddddd')
    ax.spines['bottom'].set_color('#dddddd')
    ax.tick_params(axis='both', length=0)

    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=150, facecolor='white', edgecolor='none')
    plt.close(fig)
    buf.seek(0)
    return base64.b64encode(buf.read()).decode('utf-8')