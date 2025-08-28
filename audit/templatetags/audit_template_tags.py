import datetime
from django import template
from django.forms.boundfield import BoundField

from audit.models import *

register = template.Library()

@register.filter
def is_tracking(subtheme, user):
    return subtheme.usercategory_set.filter(user=user, is_tracking=True).exists()

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)

@register.filter(name="as_integer")
def as_integer(value):
    try:
        return int(value)
    except (ValueError, TypeError):
        return value
def check_user_answers_status(category, user):
    questions = Question.objects.filter(category=category).exclude(question__isnull=True)
        
    total_questions = questions.count()
    answered_questions = UserAnswer.objects.filter(user=user, question__in=questions).count()

    if total_questions == 0:
        return "fully_answered"
    if answered_questions == 0:
        return "not_answered"
    elif answered_questions < total_questions:
        return "partially_answered"
    else:
        return "fully_answered"


def check_user_answers_status(category, user):

    questions = Question.objects.filter(category=category).exclude(question__isnull=True).exclude(question__exact='')
    total_questions = questions.count()
    total_questions = total_questions / 2
    answered_questions = UserAnswer.objects.filter(user=user, question__in=questions).count()
    
    if total_questions == 0:
        return "fully_answered"
    if answered_questions == 0:
        return "not_answered"
    elif answered_questions < total_questions:
        return "partially_answered"
    else:
        return "fully_answered"

@register.simple_tag
def has_unanswered_questions(category_id, user_id, request):
    category = Category.objects.get(id=category_id)
    user = User.objects.get(id=user_id)
    status = check_user_answers_status(category, user)
    return status in ["not_answered", "partially_answered"]

@register.simple_tag
def is_fully_answered(category_id, user_id, request):
    category = Category.objects.get(id=category_id)
    user = User.objects.get(id=user_id)
    status = check_user_answers_status(category, user)
    return status == "fully_answered"

@register.filter(name='add_class')
def add_class(value, arg):
    if isinstance(value, BoundField):
        return value.as_widget(attrs={'class': arg})
    return value

@register.filter(name="to_int")
def to_int(value):
    try:
        return int(value)
    except ValueError:
        return value
    

@register.filter(name="to_float")
def to_float(value):
    try:
        return float(value)
    except ValueError:
        return value

@register.filter
def to_time(value):
    if isinstance(value, datetime.time):
        return value
    try:
        return datetime.datetime.strptime(value, "%H:%M").time()
    except ValueError:
        return None

LIKERT3_MAP_EN = {
    1: "Disagree",
    2: "Neutral",
    3: "Agree",
}
LIKERT3N_MAP_EN = {
    3: "Disagree",
    2: "Neutral",
    1: "Agree",
}
LIKERT5_MAP_EN = {
    1: "Strongly Disagree",
    2: "Disagree",
    3: "Neutral",
    4: "Agree",
    5: "Strongly Agree",
}
LIKERT5N_MAP_EN = {
    5: "Strongly Disagree",
    4: "Disagree",
    3: "Neutral",
    2: "Agree",
    1: "Strongly Agree",
}
LIKERT7_MAP_EN = {
    1: "Very Poor",
    2: "Poor",
    3: "More Poor than Good",
    4: "Neutral",
    5: "More Good than Poor",
    6: "Good",
    7: "Very Good",
}
LIKERT7N_MAP_EN = {
    7: "Very Poor",
    6: "Poor",
    5: "More Poor than Good",
    4: "Neutral",
    3: "More Good than Poor",
    2: "Good",
    1: "Very Good",
}
LIKERT10_MAP_EN = {
    1: "Very Poor",
    2: "Poor",
    3: "Fairly Poor",
    4: "Below Average",
    5: "Average",
    6: "Slightly Above Average",
    7: "Good",
    8: "Very Good",
    9: "Excellent",
    10: "Outstanding",
}
LIKERT10N_MAP_EN = {
    10: "Very Poor",
    9: "Poor",
    8: "Fairly Poor",
    7: "Below Average",
    6: "Average",
    5: "Slightly Above Average",
    4: "Good",
    3: "Very Good",
    2: "Excellent",
    1: "Outstanding",
}

@register.filter
def Likert3_display(value):
    return LIKERT3_MAP_EN.get(int(value), value)

@register.filter
def Likert3N_display(value):
    return LIKERT3N_MAP_EN.get(int(value), value)

@register.filter
def Likert5_display(value):
    return LIKERT5_MAP_EN.get(int(value), value)

@register.filter
def Likert5N_display(value):
    return LIKERT5N_MAP_EN.get(int(value), value)

@register.filter
def Likert7_display(value):
    return LIKERT7_MAP_EN.get(int(value), value)

@register.filter
def Likert7N_display(value):
    return LIKERT7N_MAP_EN.get(int(value), value)

@register.filter
def Likert10_display(value):
    return LIKERT10_MAP_EN.get(int(value), value)

@register.filter
def Likert10N_display(value):
    return LIKERT10N_MAP_EN.get(int(value), value)