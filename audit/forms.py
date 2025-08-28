import re
from django import forms
from accounts.models import *
from audit.models import *
from django.core.exceptions import ValidationError
from datetime import datetime, time

# Likert scale options
LAKERTA3_MAP_EN = [
    (1, "Disagree"),
    (2, "Neutral"),
    (3, "Agree"),
]
LAKERTA3N_MAP_EN = [
    (3, "Disagree"),
    (2, "Neutral"),
    (1, "Agree"),
]
LAKERTA5_MAP_EN = [
    (1, "Strongly Disagree"),
    (2, "Disagree"),
    (3, "Neutral"),
    (4, "Agree"),
    (5, "Strongly Agree"),
]
LAKERTA5N_MAP_EN = [
    (5, "Strongly Disagree"),
    (4, "Disagree"),
    (3, "Neutral"),
    (2, "Agree"),
    (1, "Strongly Agree"),
]
LAKERTA7_MAP_EN = [
    (1, "Very Poor"),
    (2, "Poor"),
    (3, "More Poor than Good"),
    (4, "Neutral"),
    (5, "More Good than Poor"),
    (6, "Good"),
    (7, "Very Good"),
]
LAKERTA7N_MAP_EN = [
    (7, "Very Poor"),
    (6, "Poor"),
    (5, "More Poor than Good"),
    (4, "Neutral"),
    (3, "More Good than Poor"),
    (2, "Good"),
    (1, "Very Good"),
]
LAKERTA10_MAP_EN = [
    (1, "Very Poor"),
    (2, "Poor"),
    (3, "Fairly Poor"),
    (4, "Below Average"),
    (5, "Average"),
    (6, "Slightly Above Average"),
    (7, "Good"),
    (8, "Very Good"),
    (9, "Excellent"),
    (10, "Outstanding"),
]
LAKERTA10N_MAP_EN = [
    (10, "Very Poor"),
    (9, "Poor"),
    (8, "Fairly Poor"),
    (7, "Below Average"),
    (6, "Average"),
    (5, "Slightly Above Average"),
    (4, "Good"),
    (3, "Very Good"),
    (2, "Excellent"),
    (1, "Outstanding"),
]

def validate_time(value):
    if isinstance(value, str) and value.lower() == "null":
        return
    if isinstance(value, str):
        try:
            datetime.strptime(value, "%H:%M") 
        except ValueError:
            raise ValidationError("Invalid time format. Use HH:MM")

    elif not isinstance(value, time):
        raise ValidationError(
            "Invalid input type. Value must be a string or datetime.time object."
        )


def validate_only_numbers(value):
    if not re.match(r"^[0-9]*\.?[0-9]+$", value):
        raise ValidationError("In field only numbers are allowed.")


class WizardPage1(forms.Form):
    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        self.pk = kwargs.pop("pk", None)
        super().__init__(*args, **kwargs)

        # Likert choices
        likert_choices = {
            "Likert3": LAKERTA3_MAP_EN,
            "Likert3N": LAKERTA3N_MAP_EN,
            "Likert5": LAKERTA5_MAP_EN,
            "Likert5N": LAKERTA5N_MAP_EN,
            "Likert7": LAKERTA7_MAP_EN,
            "Likert7N": LAKERTA7N_MAP_EN,
            "Likert10": LAKERTA10_MAP_EN,
            "Likert10N": LAKERTA10N_MAP_EN,
        }

        if self.pk is not None and user is not None:
            questions = Question.objects.filter(category=self.pk)
            for question in questions:
                if question.answerType:
                    answer_type = question.answerType.type
                    question.question =  question.question
                    try:
                        previous_answer = UserAnswer.objects.get(
                            user=user, question=question
                        ).answer
                    except UserAnswer.DoesNotExist:
                        previous_answer = ""
                    field_kwargs = {
                        "label":  question.question,
                        "initial": previous_answer,
                        "required": False,
                    }
                    if answer_type in likert_choices:
                        field_kwargs["widget"] = forms.Select(attrs={'class': 'cursor-pointer'})
                        field_kwargs["choices"] = likert_choices[answer_type]
                        self.fields[question.question] = forms.ChoiceField(
                            **field_kwargs, help_text=question.description,
                        )
                    elif answer_type == "Range":
                        self.fields[question.question] = forms.CharField(
                            initial=previous_answer,
                            help_text=question.description,
                            required=False,
                            validators=[validate_only_numbers],
                            widget=forms.TextInput(attrs={'type': 'number', 'min': '0', 'max': '9999', 'step': '0.1', 'class': 'form-control'})
                        )
                    elif answer_type in ["BoolP", "BoolN"]:
                        initial_bool = (
                            previous_answer == "True"
                            if isinstance(previous_answer, str)
                            else False
                        )
                        self.fields[question.question] = forms.BooleanField(
                            required=False,
                            initial=initial_bool,
                            help_text=question.description,
                            widget=forms.CheckboxInput(attrs={'class': 'cursor-pointer'})
                        )
                    elif answer_type == "Time":
                        try:
                            if previous_answer:
                                datetime.strptime(previous_answer, "%H:%M")
                        except ValueError:
                            previous_answer = ""

                        self.fields[question.question] = forms.TimeField(
                            widget=forms.TimeInput(attrs={"type": "time"}),
                            required=False,
                            help_text=question.description,
                            validators=[validate_time],
                            input_formats=["%H:%M"],
                            initial=previous_answer,
                        )

class QuestionForm(forms.ModelForm):
    recommendations = forms.ModelMultipleChoiceField(
        queryset=Recommendation.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
    )

    class Meta:
        model = Question
        fields = ['question', 'category', 'answerType', 'min', 'max', 'time_start', 'time_end', 'weight', 'description', 'recommendations']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['time_start'].widget = forms.TimeInput(attrs={'type': 'time', 'class': 'form-control form-control-lg'})
        self.fields['time_end'].widget = forms.TimeInput(attrs={'type': 'time', 'class': 'form-control form-control-lg'})

    def clean(self):
        cleaned_data = super().clean()
        question = cleaned_data.get('question')
        category = cleaned_data.get('category')
        answer_type = cleaned_data.get('answerType')
        if not question:
            self.add_error('question', 'Question is required.')
        if not category:
            self.add_error('category', 'Category is required.')
        if not answer_type:
            self.add_error('answerType', 'Answer Type is required.')

        min_value = cleaned_data.get('min')
        max_value = cleaned_data.get('max')
        
        if answer_type in ['numeric','Range']:  
            if min_value is None or min_value == '':
                self.add_error('min', 'Min value is required for Range answer types.')
            if max_value is None or max_value == '':
                self.add_error('max', 'Max value is required for Range answer types.')
            if min_value is not None and max_value is not None:
                try:
                    min_value = float(min_value)
                    max_value = float(max_value)
                    if min_value > max_value:
                        self.add_error('max', 'Max value must be greater than or equal to Min value.')
                except ValueError:
                    self.add_error('min', 'Min and Max values must be numeric.')

        time_start = cleaned_data.get('time_start')
        time_end = cleaned_data.get('time_end')       

        if answer_type in ['Time']:  
            if time_start is None or time_start == '':
                self.add_error('time_start', 'Starting time is required for Time answer types.')
            if time_end is None or time_end == '':
                self.add_error('time_end', 'Ending time is required for Time answer types.')
            if min_value is not None and max_value is not None:
                try:

                    if time_start > time_end:
                        self.add_error('time_start', 'Starting time must be set before ending time.')
                except ValueError:
                    self.add_error('time_end', 'Starting time and ending time must be time values.')
        weight = cleaned_data.get('weight')
        if weight is None or weight == '':
            self.add_error('weight', 'Weight is required.')
        elif weight <= 0:
            self.add_error('weight', 'Weight must be a positive value.')

        return cleaned_data


class RecommendationForm(forms.ModelForm):
    categories = forms.ModelMultipleChoiceField(
        queryset=Category.objects.all(),
        widget=forms.CheckboxSelectMultiple, 
        required=True
    )

    class Meta:
        model = Recommendation
        fields = ['recommendation', 'weight', 'categories']


class CategoryForm(forms.ModelForm):
    parent = forms.ModelMultipleChoiceField(
        queryset=Category.objects.all(),
        widget=forms.CheckboxSelectMultiple,  
        required=False
    )

    class Meta:
        model = Category
        fields = ['parent', 'name', 'description']


class InputDataImportForm(forms.Form):
    file = forms.FileField()
