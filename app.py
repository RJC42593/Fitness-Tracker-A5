import os
import secrets
from pathlib import Path

from dotenv import load_dotenv
from flask import (
    Flask,
    abort,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from pymongo.errors import PyMongoError

from database import init_database
from progress import build_progress_chart
from workouts import (
    EXERCISES,
    exercise_choices,
    exercise_progress,
    find_workout,
    list_workouts,
    save_workout,
    validate_workout,
)


def create_app(test_config=None):
    settings_file = Path(__file__).with_name('.env')
    load_dotenv(settings_file, interpolate=False)

    app = Flask(__name__)
    app.secret_key = os.getenv('SECRET_KEY') or secrets.token_hex(32)
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
    app.config['MONGODB_URI'] = os.getenv('MONGODB_URI', '').strip()
    app.config['MONGODB_DB'] = os.getenv('MONGODB_DB', 'fitness_tracker').strip()

    if test_config is not None:
        app.config.update(test_config)

    init_database(app)

    @app.get('/')
    def home():
        return render_template('home.html', title='Home')

    @app.route('/record', methods=['GET', 'POST'])
    def record():
        session.setdefault('csrf', secrets.token_hex(32))
        errors = {}
        status = 200

        if request.method == 'POST':
            values = request.form.to_dict()
            submitted_token = values.get('csrf', '').encode()
            expected_token = session['csrf'].encode()

            if not secrets.compare_digest(submitted_token, expected_token):
                abort(400, 'Form expired. Reload the Record Workout page.')

            workout, errors = validate_workout(values)

            if errors:
                status = 422
            else:
                try:
                    workout_id = save_workout(workout)
                except (RuntimeError, PyMongoError):
                    errors['storage'] = (
                        'We could not confirm your workout was saved. '
                        'Your entries are preserved. '
                        'Check your saved records before retrying.'
                    )
                    status = 503
                else:
                    saved_url = url_for('saved_workout', workout_id=workout_id)
                    return redirect(saved_url, code=303)
        else:
            values = {'mode': 'existing'}

        return (
            render_template(
                'record.html',
                title='Record Workout',
                values=values,
                errors=errors,
                exercises=EXERCISES,
            ),
            status,
        )

    @app.get('/history')
    def history():
        try:
            workouts = list_workouts()
        except (RuntimeError, PyMongoError):
            return (
                render_template(
                    'message.html',
                    title='Workout History unavailable',
                    message=(
                        'We could not load your saved workouts. '
                        'Reload this page when your connection is available.'
                    ),
                ),
                503,
            )

        return render_template(
            'history.html',
            title='Workout History',
            workouts=workouts,
        )

    @app.get('/progress')
    def progress():
        try:
            exercises = exercise_choices()
            exercise = request.args.get('exercise', 'Bench Press')

            if exercise not in exercises:
                abort(400, 'Choose an exercise from the progress page.')

            workouts = exercise_progress(exercise)
        except (RuntimeError, PyMongoError):
            return (
                render_template(
                    'message.html',
                    title='Exercise Progress unavailable',
                    message=(
                        'We could not load your exercise progress. '
                        'Reload this page when your connection is available.'
                    ),
                ),
                503,
            )

        chart_image = build_progress_chart(workouts)

        return render_template(
            'progress.html',
            title='Track Exercise Progress',
            exercises=exercises,
            exercise=exercise,
            workouts=workouts,
            chart_image=chart_image,
        )

    @app.get('/workouts/<workout_id>')
    def saved_workout(workout_id):
        try:
            workout = find_workout(workout_id)
        except (RuntimeError, PyMongoError):
            return (
                render_template(
                    'message.html',
                    title='Workout details unavailable',
                    message=(
                        'We could not load this workout. '
                        'If you just saved it, the save may already have completed. '
                        'Reload this page when your connection is available.'
                    ),
                ),
                503,
            )

        if workout is None:
            abort(404, 'Workout not found.')

        return render_template(
            'saved.html',
            title='Saved Workout',
            workout=workout,
        )

    return app
