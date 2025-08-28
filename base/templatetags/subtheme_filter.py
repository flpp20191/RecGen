import datetime
from django import template
from django.conf import settings
from audit.models import Question, UserAnswer, Category
from django.contrib.auth.models import User
from django.forms.boundfield import BoundField
register = template.Library()


@register.filter
def is_tracking(subtheme, user):
    return subtheme.usercategory_set.filter(user=user, is_tracking=True).exists()


@register.filter(name="to_int")
def to_int(value):
    try:
        return int(value)
    except ValueError:
        return value


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
    subtheme = Category.objects.get(id=category_id)
    user = User.objects.get(id=user_id)
    status = check_user_answers_status(subtheme, user)
    return status in ["not_answered", "partially_answered"]

@register.simple_tag
def is_partially_answered(category_id, user_id, request):
    subtheme = Category.objects.get(id=category_id)
    user = User.objects.get(id=user_id)
    status = check_user_answers_status(subtheme, user)
    return status == "partially_answered"

@register.simple_tag
def is_fully_answered(category_id, user_id, request):
    subtheme = Category.objects.get(id=category_id)
    user = User.objects.get(id=user_id)
    status = check_user_answers_status(subtheme, user)
    return status == "fully_answered"

@register.filter
def to_time(value):
    if isinstance(value, datetime.time):
        return value
    try:
        return datetime.datetime.strptime(value, "%H:%M").time()
    except ValueError:
        return None


@register.filter(name="time_in_range")
def time_in_range(value, arg):
    """
    Check if the time value is within the range specified by arg ("start_time, end_time").
    Both start_time and end_time are expected to be python time objects.
    """
    user_time = to_time(value)
    if user_time and arg:
        time_start, time_end = arg.split(",")
        time_start = to_time(time_start)
        time_end = to_time(time_end)
        if time_start and time_end:
            return time_start <= user_time <= time_end
    return False


@register.filter
def to_time_no_seconds(value):
    try:
        # Assuming time is in '10:30 a.m.' format, convert it to a time object
        time_obj = datetime.strptime(value, "%I:%M %p")
        return time_obj.strftime("%H:%M")
    except ValueError:
        return value



@register.filter(name='subtheme_button_class')
def subtheme_button_class(subtheme, user):
    # Utilize previously defined filters or direct queries to determine the user's progress
    if subtheme.has_unanswered_questions(user):
        return 'unanswered-button'
    elif subtheme.is_partially_answered(user):
        return 'partially-answered-button'
    else:
        return 'answered-button'

@register.filter(name='subtheme_button_text')
def subtheme_button_text(subtheme, user):
    # Again, checking the user's progress to determine the appropriate button text
    if subtheme.has_unanswered_questions(user):
        return 'Sākt pašnovērtēšanu'
    elif subtheme.is_partially_answered(user):
        return 'Turpināt pašnovērtēšanu'
    else:
        return 'Pārskatīt pašnovērtēšanu'
    



@register.filter(name='has_group')
def has_group(user, group_name):
    if user.is_authenticated:
        return user.groups.filter(name=group_name).exists()
    return False



@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)

@register.filter
def get_keys(dictionary):
    return dictionary.keys()

@register.filter(name='add_class')
def add_class(value, arg):
    if isinstance(value, BoundField):
        return value.as_widget(attrs={'class': arg})
    return value


@register.filter
def attr(obj, attribute_name):
    return getattr(obj, attribute_name, None)