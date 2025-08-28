document.addEventListener("DOMContentLoaded", function () {
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    if (tooltipTriggerList.length > 0) {
        var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    }

    const answerTypeField = document.getElementById('id_answerType');
    const minField = document.getElementById('id_min');
    const maxField = document.getElementById('id_max');
    const timeStartField = document.getElementById('id_time_start');
    const timeEndField = document.getElementById('id_time_end');
    const weightField = document.getElementById('id_weight');
    const saveButton = document.querySelector('.btn-submit-custom');
    const questionInput = document.getElementById('id_question');
    const form = document.querySelector("form");

    let originalAnswerType = answerTypeField ? answerTypeField.value : null;

    if (answerTypeField) {
        answerTypeField.addEventListener('change', handleAnswerTypeChange);
        handleAnswerTypeChange();
    }

    if (questionInput) {
        questionInput.addEventListener('input', validateForm);
    }

    if (weightField) {
        weightField.addEventListener('input', validateForm);
    }

    if (minField) {
        minField.addEventListener('input', validateForm);
    }

    if (maxField) {
        maxField.addEventListener('input', validateForm);
    }

    if (timeStartField) {
        timeStartField.addEventListener('input', validateForm);
    }

    if (timeEndField) {
        timeEndField.addEventListener('input', validateForm);
    }

    if (form) {
        form.addEventListener('submit', function (event) {
            if (answerTypeField && answerTypeField.value !== originalAnswerType) {
                event.preventDefault(); // Prevent default form submission

                const confirmationModal = new bootstrap.Modal(document.getElementById('confirmationModal'), {});
                confirmationModal.show();

                // Ensure the event listener for the confirm button is not duplicated
                document.getElementById('confirmChangeButton').onclick = function () {
                    confirmationModal.hide();
                    originalAnswerType = answerTypeField.value;
                    form.submit(); // Proceed with form submission
                };
            } else {
                if (!validateForm()) {
                    event.preventDefault();
                    alert("Please ensure all required fields are filled out correctly.");
                }
            }
        });
    }

    function handleAnswerTypeChange() {
        if (!answerTypeField) return;

        const selectedType = answerTypeField.options[answerTypeField.selectedIndex].text;

        if (selectedType.includes('Likert')) {
            minField.disabled = true;
            maxField.disabled = true;
            timeStartField.disabled = true;
            timeEndField.disabled = true;
        } else if (selectedType === 'Range') {
            minField.disabled = false;
            maxField.disabled = false;
            timeStartField.disabled = true;
            timeEndField.disabled = true;
        } else if (selectedType === 'Time') {
            minField.disabled = true;
            maxField.disabled = true;
            timeStartField.disabled = false;
            timeEndField.disabled = false;
        } else if (selectedType.includes('Bool')) {
            minField.disabled = true;
            maxField.disabled = true;
            timeStartField.disabled = true;
            timeEndField.disabled = true;
        } else {
            minField.disabled = false;
            maxField.disabled = false;
            timeStartField.disabled = false;
            timeEndField.disabled = false;
        }

        validateForm();
    }

    function validateForm() {
        let isValid = true;

        if (questionInput && questionInput.value.trim() === '') {
            questionInput.classList.add('is-invalid');
            isValid = false;
        } else {
            questionInput.classList.remove('is-invalid');
        }

        const selectedType = answerTypeField ? answerTypeField.options[answerTypeField.selectedIndex].text : '';
        if (selectedType === 'Range') {
            if (!minField.disabled && (minField.value.trim() === '' || isNaN(minField.value))) {
                minField.classList.add('is-invalid');
                isValid = false;
            } else {
                minField.classList.remove('is-invalid');
            }

            if (!maxField.disabled && (maxField.value.trim() === '' || isNaN(maxField.value))) {
                maxField.classList.add('is-invalid');
                isValid = false;
            } else {
                maxField.classList.remove('is-invalid');
            }

            if (!minField.disabled && !maxField.disabled && minField.value && maxField.value && parseFloat(minField.value) > parseFloat(maxField.value)) {
                maxField.classList.add('is-invalid');
                isValid = false;
            }
        }

        if (selectedType === 'Time') {
            if (!timeStartField.disabled && timeStartField.value.trim() === '') {
                timeStartField.classList.add('is-invalid');
                isValid = false;
            } else {
                timeStartField.classList.remove('is-invalid');
            }

            if (!timeEndField.disabled && timeEndField.value.trim() === '') {
                timeEndField.classList.add('is-invalid');
                isValid = false;
            } else {
                timeEndField.classList.remove('is-invalid');
            }

            if (timeStartField.value && timeEndField.value && timeStartField.value > timeEndField.value) {
                timeStartField.classList.add('is-invalid');
                timeEndField.classList.add('is-invalid');
                isValid = false;
            }
        }

        if (weightField && (weightField.value.trim() === '' || isNaN(weightField.value) || parseFloat(weightField.value) <= 0)) {
            weightField.classList.add('is-invalid');
            isValid = false;
        } else {
            weightField.classList.remove('is-invalid');
        }

        if (saveButton) {
            saveButton.disabled = !isValid;
        }

        return isValid;
    }
});
