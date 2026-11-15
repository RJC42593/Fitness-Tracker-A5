from datetime import date
from math import isfinite

from bson import ObjectId
from pymongo import timeout

from database import get_database

EXERCISES = ['Bench Press', 'Shoulder Press', 'Squat', 'Deadlift']


def validate_workout(values):
    errors = {}
    workout = {}
    mode = values.get('mode', '')

    if mode == 'existing':
        exercise_field = 'existing'
    else:
        exercise_field = 'manual'

    exercise = values.get(exercise_field, '').strip()

    if mode not in ('existing', 'manual') or not exercise or len(exercise) > 80:
        errors['exercise'] = (
            'Please select or enter an exercise name (1–80 characters).'
        )
        if mode == 'existing' and not exercise:
            errors['exercise'] = 'Please select an exercise.'
    elif mode == 'existing' and exercise not in EXERCISES:
        errors['exercise'] = 'Please select an available exercise.'
    else:
        workout['exercise'] = exercise

    try:
        workout_date = values.get('date', '')
        workout['date'] = date.fromisoformat(workout_date).isoformat()
    except ValueError:
        errors['date'] = 'Please enter a valid workout date before saving your workout.'
        if not workout_date:
            errors['date'] = 'Please enter a workout date.'

    number_fields = [('sets', 'sets'), ('reps', 'repetitions'), ('weight', 'weight')]

    for field, label in number_fields:
        raw = values.get(field, '').strip()

        if not raw:
            if field == 'weight':
                errors[field] = 'Please enter a weight before saving your workout.'
            elif field == 'sets':
                errors[field] = 'Please enter the number of sets.'
            else:
                errors[field] = 'Please enter the repetitions.'
            continue

        if field == 'weight':
            minimum = 0
        else:
            minimum = 1

        try:
            if field == 'weight':
                number = float(raw)
            else:
                number = int(raw)

            if not isfinite(number) or not minimum <= number <= 10000:
                raise ValueError

            workout[field] = number
        except (ValueError, OverflowError):
            if field == 'weight':
                number_type = 'a number'
            else:
                number_type = 'a whole number'

            errors[field] = (
                f'{label.capitalize()} must be {number_type} '
                f'from {minimum} to 10000.'
            )

    return workout, errors


def save_workout(workout):
    with timeout(5):
        result = get_database()['workouts'].insert_one(dict(workout))
    if not result.acknowledged:
        raise RuntimeError('Workout write was not acknowledged.')
    return str(result.inserted_id)


def find_workout(workout_id):
    if not ObjectId.is_valid(workout_id):
        return None
    with timeout(5):
        return get_database()['workouts'].find_one({'_id': ObjectId(workout_id)})


def list_workouts():
    with timeout(5):
        cursor = get_database()['workouts'].find().sort([('date', -1), ('_id', -1)])
        return list(cursor)


def exercise_choices():
    with timeout(5):
        saved_names = get_database()['workouts'].distinct('exercise')
    return sorted(set(EXERCISES + saved_names), key=str.casefold)


def exercise_progress(exercise):
    with timeout(5):
        collection = get_database()['workouts']
        cursor = collection.find({'exercise': exercise})
        cursor = cursor.sort([('date', 1), ('_id', 1)])
        return list(cursor)
