from base64 import b64encode
from datetime import date, timedelta
from io import BytesIO
from math import ceil

from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.dates import DateFormatter, DayLocator
from matplotlib.figure import Figure


def build_progress_chart(workouts):
    if not workouts:
        return None

    dates = []
    weights = []

    for workout in workouts:
        dates.append(date.fromisoformat(workout['date']))
        weights.append(workout['weight'])

    figure = Figure(figsize=(8, 4), dpi=90)
    canvas = FigureCanvasAgg(figure)
    axes = figure.subplots()

    axes.plot(dates, weights, marker='o', color='#2454cf', linewidth=2)
    axes.set_xlabel('Workout date')
    axes.set_ylabel('Weight (lbs)')
    axes.set_ylim(bottom=0, top=max(1, max(weights) * 1.1))
    axes.grid(True, alpha=0.3)

    day_span = (dates[-1] - dates[0]).days
    tick_spacing = max(1, ceil(day_span / 5))
    axes.xaxis.set_major_locator(DayLocator(interval=tick_spacing))
    axes.xaxis.set_major_formatter(DateFormatter('%Y-%m-%d'))

    if dates[0] == dates[-1]:
        axes.set_xlim(dates[0] - timedelta(days=1), dates[0] + timedelta(days=1))

    axes.tick_params(axis='x', labelrotation=30)
    figure.subplots_adjust(left=0.12, right=0.97, bottom=0.25, top=0.95)

    with BytesIO() as image:
        canvas.print_png(image, pil_kwargs={'compress_level': 1})
        return b64encode(image.getvalue()).decode('ascii')
