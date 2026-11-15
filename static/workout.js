const workoutForm = document.getElementById('workout-form');

if (workoutForm !== null) {
    const clearDialog = document.getElementById('clear-dialog');
    const exerciseModes = workoutForm.querySelectorAll('input[name="mode"]');

    function updateExerciseMode() {
        const selectedMode = workoutForm.querySelector('input[name="mode"]:checked');
        const manualSelected = selectedMode.value === 'manual';

        workoutForm.elements.existing.disabled = manualSelected;
        workoutForm.elements.manual.disabled = !manualSelected;

        if (manualSelected) {
            workoutForm.elements.existing.options[0].textContent = 'Select Option A to choose';
            workoutForm.elements.manual.placeholder = 'Enter exercise name';
        } else {
            workoutForm.elements.existing.options[0].textContent = 'Select an exercise';
            workoutForm.elements.manual.placeholder = 'Select Option B to type';
        }
    }

    function showClearDialog() {
        clearDialog.showModal();
    }

    function keepEditing() {
        clearDialog.close();
    }

    function clearWorkout() {
        const fieldNames = ['existing', 'manual', 'date', 'sets', 'reps', 'weight'];

        for (const name of fieldNames) {
            workoutForm.elements[name].value = '';
        }

        exerciseModes[0].checked = true;
        updateExerciseMode();

        const errorSummary = document.getElementById('errors');

        if (errorSummary !== null) {
            errorSummary.remove();
        }

        const errorMessages = workoutForm.querySelectorAll('.error-text');

        for (const message of errorMessages) {
            message.textContent = '';
        }

        const inputs = workoutForm.querySelectorAll('[aria-invalid]');

        for (const input of inputs) {
            input.setAttribute('aria-invalid', 'false');
        }

        clearDialog.close();
        workoutForm.elements.existing.focus();
    }

    for (const radio of exerciseModes) {
        radio.addEventListener('change', updateExerciseMode);
    }

    document.getElementById('clear-request').addEventListener('click', showClearDialog);
    document.getElementById('keep-editing').addEventListener('click', keepEditing);
    document.getElementById('clear-confirm').addEventListener('click', clearWorkout);

    updateExerciseMode();

    const errorSummary = document.getElementById('errors');

    if (errorSummary !== null) {
        errorSummary.focus();
    }
}

const exerciseSelect = document.getElementById('progress-exercise');

function updateProgress() {
    document.getElementById('progress-form').requestSubmit();
}

if (exerciseSelect !== null) {
    exerciseSelect.addEventListener('change', updateProgress);
}
