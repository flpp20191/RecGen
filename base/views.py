import json
from base.calculation_script import (
    calculate_score_percentage,
    calculate_category_score_percentage,
)
from django.shortcuts import get_object_or_404, redirect, render
from base.serializers import categorySerializer
from audit.models import *
from accounts.models import *
from django.contrib.auth.decorators import login_required
import os
from operator import itemgetter
from root.settings import (
    BASE_DIR,
    MEDIA_ROOT,
    STATICFILES_DIRS,
)
from django.views.decorators.cache import never_cache
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Count, Q
import base64
import os
import environ
env = environ.Env()
environ.Env.read_env()
def home_redirect(request):
    if request.user.is_authenticated:
        return redirect('base:Dashboard')  
    else:
        return redirect('accounts:login')  

@login_required
@never_cache
def dashboard(request):
    if request.user.is_authenticated:
        clicked_recommendation = request.COOKIES.get("clickedRecommendation", 0)
        clickedRecommendationTrueDashboard = request.COOKIES.get(
            "clickedRecommendationTrueDashboard", "false"
        )
        has_accepted_cookies_client = (
            request.COOKIES.get("has_accepted_cookies", "false") == "true"
        )
        current_user_id = request.user.id

        # Check if the user has any answers
        has_data_to_export = UserAnswer.objects.filter(user=current_user_id).exists()

        (
            answers,
            recommendation_list_tier_one_true,
            recommendation_list_tier_two_true,
            recommendation_list_tier_three_true,
            recommendation_data,
        ) = calculate_score_percentage(current_user_id)
        average_value = sum(answers.values()) / len(answers) if answers else 0
        average_value_str = "{:.2f}".format(average_value)

        category, category_data = calculate_category_score_percentage(current_user_id)
        sorted_categories_data  = dict(sorted(category_data.items(), key=lambda item: item[1]['percentage']))
        no_categories = False
        if not sorted_categories_data:
            no_categories = True
        sorted_categorys = sorted(category.items(), key=itemgetter(1))
        try:
            user_information = UserInformation.objects.get(user_information=current_user_id)
        except UserInformation.DoesNotExist:
            user_information = None

    nonce = base64.b64encode(os.urandom(16)).decode('utf-8')

    categories = Category.objects.annotate(
        num_answers=Count("question__useranswer", filter=Q(question__useranswer__user=request.user))
    ).filter(num_answers__gt=0)
    
    recommendation_list_tier_one = Recommendation.objects.filter(
        weight__gte=60
    ).order_by("-weight")
    recommendation_list_tier_two = Recommendation.objects.filter(
        weight__gte=30, weight__lte=59
    ).order_by("-weight")
    recommendation_list_tier_three = Recommendation.objects.filter(
        weight__lte=29
    ).order_by("-weight")

    clicked_recommendation_id = int(clicked_recommendation)

    recommendation_list_tier_one_ids = [r.id for r in recommendation_list_tier_one]
    recommendation_list_tier_two_ids = [r.id for r in recommendation_list_tier_two]
    recommendation_list_tier_three_ids = [r.id for r in recommendation_list_tier_three]

    is_in_tier_one = clicked_recommendation_id in recommendation_list_tier_one_ids
    is_in_tier_two = clicked_recommendation_id in recommendation_list_tier_two_ids
    is_in_tier_three = clicked_recommendation_id in recommendation_list_tier_three_ids
    Recommendation_thershold = int(env("RECOMMENDATION_THRESHOLD"))


    recommendation_list_tier_one_filtered = []
    for rec_text, rec_data in recommendation_list_tier_one_true.items():
        id = rec_data.get("id")
        percentage = rec_data.get("percentage", 9999)
        if percentage < Recommendation_thershold:
            recommendation_list_tier_one_filtered.append({
                "rec_id":id,
                "recommendation_text": rec_text,
                "percentage": percentage
            })
    
    no_recommendation_1 = (len(recommendation_list_tier_one_filtered) == 0)

    # Repeat for tier_two, tier_three with same pattern...
    recommendation_list_tier_two_filtered = []
    for rec_text, rec_data in recommendation_list_tier_two_true.items():
        id = rec_data.get("id")
        percentage = rec_data.get("percentage", 9999)
        if percentage < Recommendation_thershold:
            recommendation_list_tier_two_filtered.append({
                "rec_id":id,
                "recommendation_text": rec_text,
                "percentage": percentage
            })
    no_recommendation_2 = (len(recommendation_list_tier_two_filtered) == 0)

    recommendation_list_tier_three_filtered = []
    for rec_text, rec_data in recommendation_list_tier_three_true.items():

        percentage = rec_data.get("percentage", 9999)
        id = rec_data.get("id")
        if percentage < Recommendation_thershold:
            recommendation_list_tier_three_filtered.append({
                "rec_id":id,
                "recommendation_text": rec_text,
                "percentage": percentage
            })
    no_recommendation_3 = (len(recommendation_list_tier_three_filtered) == 0)
    context = {
        "categories": categories,
        "answers": answers,
        "recommendation_data": recommendation_data,
        "sorted_categorys": sorted_categorys,
        "category_data": category_data,
        "recommendation_list_tier_one": recommendation_list_tier_one,
        "recommendation_list_tier_two": recommendation_list_tier_two,
        "recommendation_list_tier_three": recommendation_list_tier_three,
        "recommendation_list_tier_one_true": recommendation_list_tier_one_filtered,
        "recommendation_list_tier_two_true": recommendation_list_tier_two_filtered,
        "recommendation_list_tier_three_true": recommendation_list_tier_three_filtered,
        "no_recommendation_1":no_recommendation_1,
        "no_recommendation_2":no_recommendation_2,
        "no_recommendation_3":no_recommendation_3,
        "has_accepted_cookies_client": has_accepted_cookies_client,
        "clicked_recommendation": clicked_recommendation,
        "is_in_tier_one": is_in_tier_one,
        "is_in_tier_two": is_in_tier_two,
        "is_in_tier_three": is_in_tier_three,
        "clickedRecommendationTrueDashboard": clickedRecommendationTrueDashboard,
        "no_categories": no_categories,
        "sorted_categories_data": sorted_categories_data,
        "nonce": nonce, 
        "average_value": average_value_str,
        "has_data_to_export": has_data_to_export, 
        "Recommendation_thershold": Recommendation_thershold,
    }
    return render(request, "base/dashboard.html", context)

def main(request):
    return render(request, "base/main.html")

class categorysListView(APIView):
    def get(self, request, format=None):
        categorys = Category.objects.all()
        serializer = categorySerializer(categorys, many=True)
        return Response(serializer.data)
