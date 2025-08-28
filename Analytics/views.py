from time import localtime
from django.conf import settings
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
import pandas as pd
from django.http import HttpResponse, JsonResponse
from django.utils import timezone
from django.contrib.auth.models import User, Group
from django.contrib.auth.decorators import user_passes_test, login_required
from base.calculation_script import calculate_score_percentage
from audit.models import *
from accounts.models import *
from django.utils.dateformat import format
from django.utils.timezone import localtime
from django.contrib import messages
import environ
env = environ.Env()
environ.Env.read_env()
def export_user_information_data(request):
    questions = Question.objects.all()

    data = []
    
    analyst_group = Group.objects.get(name='Analyst')
    excluded_users = User.objects.filter(is_superuser=True)
    users_information = UserInformation.objects.exclude(user_information__in=excluded_users)

    for user_information in users_information:
        user = user_information.user_information  

        user_data = {
            'Users Name': user,
            'Address': user_information.address,  
            'Contact Number': user_information.contact_number,
            'Contact Email': user.email,  
        }
        
        for question in questions:
            user_answer = UserAnswer.objects.filter(user=user, question=question).first()
            user_data[question.question] = user_answer.answer if user_answer else ""
        
        data.append(user_data)

    df = pd.DataFrame(data)

    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename=school_data_{timezone.now().strftime("%Y%m%d_%H%M%S")}.xlsx'

    with pd.ExcelWriter(response, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Schools')

    return response

@user_passes_test(lambda u: u.is_superuser or u.groups.filter(name='Analyst').exists())
def select_data_to_export(request):
    if request.method == 'POST':
        selected_questions = request.POST.getlist('questions')
        selected_categories = request.POST.getlist('categories')        
        if selected_categories:
            category_questions = Question.objects.filter(category__in=selected_categories)
            questions = Question.objects.filter(id__in=selected_questions) | category_questions
        else:
            questions = Question.objects.filter(id__in=selected_questions)
        
        data = []
        excluded_users = User.objects.filter(is_superuser=True) 
        
        users_information = UserInformation.objects.exclude(user_information__in=excluded_users)

        for user_information in users_information:
            user = user_information.user_information  

            user_data = {
                'Users Name': user,
                'Address': user_information.address,
                'Contact Number': user_information.contact_number,
                'Contact Email': user_information.contact_email,
            }
            for question in questions:
                user_answer = UserAnswer.objects.filter(user=user, question=question).first()
                user_data[question.question] = user_answer.answer if user_answer else ""
            data.append(user_data)

        df = pd.DataFrame(data)

        response = HttpResponse(
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = f'attachment; filename=selected_data_{timezone.now().strftime("%Y%m%d_%H%M%S")}.xlsx'

        with pd.ExcelWriter(response, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Selected Data')

        return response

    questions = Question.objects.all()
    categories = Category.objects.all()
    return render(request, 'Analytics/select_data_to_export.html', {
        'questions': questions,
        'categories': categories,
    })

@login_required
def user_information_detail(request, user_id):
    user_information = get_object_or_404(UserInformation, pk=user_id)
    user_answers = UserAnswer.objects.filter(user=user_id)

    recommendations = Recommendation.objects.filter(
        question__useranswer__user=user_id
    ).distinct()

    (
        answers,
        recommendation_list_tier_one_true,
        recommendation_list_tier_two_true,
        recommendation_list_tier_three_true,
        recommendation_data,
    ) = calculate_score_percentage(user_id)

    average_value = sum(answers.values()) / len(answers) if answers else 0
    average_value_str = "{:.2f}".format(average_value)
    recommendation_list_tier_one = Recommendation.objects.filter(
        weight__gte=60
    ).order_by("-weight")
    recommendation_list_tier_two = Recommendation.objects.filter(
        weight__gte=30, weight__lte=59
    ).order_by("-weight")
    recommendation_list_tier_three = Recommendation.objects.filter(
        weight__lte=29
    ).order_by("-weight")


    return render(request, 'Analytics/user_detail.html', {
        'user_information': user_information,
        'user_answers': user_answers,
        'recommendations': recommendations,
        "recommendation_list_tier_one": recommendation_list_tier_one,
        "recommendation_list_tier_two": recommendation_list_tier_two,
        "recommendation_list_tier_three": recommendation_list_tier_three,
        "recommendation_list_tier_one_true": recommendation_list_tier_one_true,
        "recommendation_list_tier_two_true": recommendation_list_tier_two_true,
        "recommendation_list_tier_three_true": recommendation_list_tier_three_true,

        'average_value': average_value_str,
    })


@login_required
def user_information_summary(request):
    excluded_users = User.objects.filter(is_superuser=True)
    users_information = UserInformation.objects.exclude(user_information__in=excluded_users)
    Recommendation_thershold = int(env("RECOMMENDATION_THRESHOLD"))
    user_data = []
    total_questions = Question.objects.count()
    for user_information in users_information:
        user_instance = user_information.user_information

        answered_questions = UserAnswer.objects.filter(user=user_instance).count()

        if total_questions > 0:
            percentage_answered = (answered_questions / total_questions) * 100
        else:
            percentage_answered = 0

        (
            answers,
            recommendation_list_tier_one_true,
            recommendation_list_tier_two_true,
            recommendation_list_tier_three_true,
            recommendation_data,
        ) = calculate_score_percentage(user_instance.id)  

        average_value = sum(answers.values()) / len(answers) if answers else 0
        average_value_str = "{:.2f}".format(average_value)
        
        is_analyst = user_instance.groups.filter(name='Analyst').exists()

        user_data.append({
            'id': user_instance.id, 
            'name': user_information.name,  
            'username': user_instance.username,  
            'answered_percentage': round(percentage_answered, 2),
            'average_value': average_value_str,
            'is_analyst': is_analyst,
        })
    return render(request, 'Analytics/users_summary.html', {
        'user_data': user_data,
        'is_superuser': request.user.is_superuser,
        'Recommendation_thershold':Recommendation_thershold,
    })


@login_required
def toggle_analyst_group(request):
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)

    user_id = request.POST.get('user_id')
    print(user_id)
    user = User.objects.get(id=user_id)
    print(user)
    try:
        user = User.objects.get(id=user_id)
        print("User found")
    except User.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'User not found'}, status=404)

    analyst_group, created = Group.objects.get_or_create(name='Analyst')

    if request.POST.get('action') == 'add':
        user.groups.add(analyst_group)
        status = 'added'
    elif request.POST.get('action') == 'remove':
        user.groups.remove(analyst_group)
        status = 'removed'
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid action'}, status=400)

    return JsonResponse({'status': status, 'message': f'User {status} from analyst group'})


