from accounts.models import *
from audit.models import *
from collections import defaultdict
from django.db.models import Q
from datetime import datetime, time


def check_within_range(value, min_value, max_value):
    if value == '':
        return False 
    
    try:
        value = float(value)
    except ValueError:
        raise ValueError(f"Invalid value for conversion to float: {value}")

    if min_value is not None:
        min_value = float(min_value)
    if max_value is not None:
        max_value = float(max_value)

    return min_value <= value <= max_value if min_value is not None and max_value is not None else True

def is_time_within_range(time_str, start_time_str, end_time_str, time_format="%H:%M"):
    if time_str == "null":
        print("time_str is 'null'")
        return 0

    try:
        # Check if time_str is already a time object, otherwise parse it
        if isinstance(time_str, time):
            time_obj = time_str
        else:
            time_obj = datetime.strptime(time_str, time_format).time()
    except ValueError as e:
        print("Error parsing time:", e)
        return 0

    try:
        # Check if start_time_str and end_time_str are already time objects, otherwise parse them
        if isinstance(start_time_str, time):
            start_time = start_time_str
        else:
            start_time = datetime.strptime(start_time_str, time_format).time()
        
        if isinstance(end_time_str, time):
            end_time = end_time_str
        else:
            end_time = datetime.strptime(end_time_str, time_format).time()
    except ValueError as e:
        print("Error parsing range times:", e)
        return 0

    within_range = start_time <= time_obj <= end_time
    return 1 if within_range else 0

def calculate_reversed_value(x, n):
    try:
        x = float(x)
        n = float(n)
    except ValueError:
        return 0
    if x < 1 or x > n:
        return 0
    return 1 - ((x - 1) / (n - 1))

def calculate_value(x, n):
    try:
        x = float(x)
        n = float(n)
    except ValueError:
        return 0
    if x < 1 or x > n:
        return 0
    return (x - 1) / (n - 1)

def calculate_score_percentage(current_user_id):
    answers = UserAnswer.objects.filter(user_id=current_user_id)
    recommendation_scores = defaultdict(float)
    recommendation_weights = defaultdict(float)
    recommendation_data = defaultdict(
        lambda: {"id": None, "percentage": 0.0, "score": 0.0, "weight": 0.0, "total_weight": 0.0, "questions": []}
    )

    for answer in answers:
        question = answer.question
        recommendations = question.recommendations.all()
        if str(question.answerType) == "Range":
            answerValue = check_within_range(answer.answer, question.min, question.max)
        elif str(question.answerType) == "BoolP":
            answerValue = 0 if answer.answer == "False" else 1
        elif str(question.answerType) == "BoolN":
            answerValue = 0 if answer.answer == "True" else 1
        elif str(question.answerType) == "Likert3":
            answerValue = calculate_value(answer.answer, 3)
        elif str(question.answerType) == "Likert3N":
            answerValue = calculate_reversed_value(answer.answer, 3)
        elif str(question.answerType) == "Likert5":
            answerValue = calculate_value(answer.answer, 5)
        elif str(question.answerType) == "Likert5N":
            answerValue = calculate_reversed_value(answer.answer, 5)
        elif str(question.answerType) == "Likert7":
            answerValue = calculate_value(answer.answer, 7)
        elif str(question.answerType) == "Likert7N":
            answerValue = calculate_reversed_value(answer.answer, 7)
        elif str(question.answerType) == "Likert10":
            answerValue = calculate_value(answer.answer, 10)
        elif str(question.answerType) == "Likert10N":
            answerValue = calculate_reversed_value(answer.answer, 10)
        elif str(question.answerType) == "Time":
            answerValue = is_time_within_range(answer.answer, question.time_start, question.time_end)
        elif answer.answer == "null":
            answerValue = 0
        else:
            try:
                answerValue = float(answer.answer)
            except (ValueError, TypeError):
                answerValue = 0

        for recommendation in recommendations:
            print(recommendation)
            weight = float(question.weight if question.weight is not None else 1.0)
            recommendation_scores[str(recommendation)] += answerValue * weight
            recommendation_weights[str(recommendation)] += weight
            recommendation_data[str(recommendation)]["questions"].append(
                {
                    "question": question.question,
                    "user_answer": answer.answer,
                    "question_type": question.answerType,
                    "min_value": question.min,
                    "max_value": question.max,
                    "time_start": question.time_start,
                    "time_end": question.time_end,
                }
            )
            recommendation_data[str(recommendation)]["total_weight"] += weight
            recommendation_data[str(recommendation)]["id"] = recommendation.id
            recommendation_data[str(recommendation)]["recommendation_weight"] = recommendation.weight

    recommendation_percentages = {
        k: round(((v / recommendation_data[k]["total_weight"]) * 100), 2)
        if recommendation_data[k]["total_weight"] > 0 else 0
        for k, v in recommendation_scores.items()
    }

    for recommendation, data in recommendation_data.items():
        data["score"] = recommendation_scores[recommendation]
        data["weight"] = recommendation_weights[recommendation]
        data["percentage"] = recommendation_percentages.get(recommendation, 0.0)

    combined_data = {
        recommendation: {
            "id": data["id"],
            "percentage": data["percentage"],
            "score": data["score"],
            "weight": data["weight"],
            "recommendation_weight": data["recommendation_weight"],
            "questions": data["questions"],
        }
        for recommendation, data in recommendation_data.items()
    }

    tier_one = {
        recommendation: data
        for recommendation, data in combined_data.items()
        if data["recommendation_weight"] >= 60
    }
    tier_two = {
        recommendation: data
        for recommendation, data in combined_data.items()
        if 30 <= data["recommendation_weight"] < 60
    }
    tier_three = {
        recommendation: data
        for recommendation, data in combined_data.items()
        if data["recommendation_weight"] < 30
    }

    return (
        dict(recommendation_percentages),
        tier_one,
        tier_two,
        tier_three,
        combined_data,
    )

def calculate_category_score_percentage(current_user_id):
    user = User.objects.get(pk=current_user_id)
    tracking_categories = Category.objects.filter(
        usercategory__user=user, usercategory__is_tracking=True
    )
    answers = UserAnswer.objects.filter(
        Q(user_id=current_user_id) & Q(question__category__in=tracking_categories)
    )
    
    category_scores = defaultdict(float)
    category_weights = defaultdict(float)
    category_data = defaultdict(
        lambda: {"id": None, "percentage": 0, "score": 0, "weight": 0, "total_weight": 0, "questions": []}
    )

    for answer in answers:
        question = answer.question
        category = question.category

        if category in tracking_categories:
            if str(question.answerType) == "Range":
                answerValue = check_within_range(answer.answer, question.min, question.max)
            elif str(question.answerType) == "BoolP":
                answerValue = 0 if answer.answer == "False" else 1
            elif str(question.answerType) == "BoolN":
                answerValue = 0 if answer.answer == "True" else 1
            elif str(question.answerType) == "Likert3":
                answerValue = calculate_value(answer.answer, 3)
            elif str(question.answerType) == "Likert3N":
                answerValue = calculate_reversed_value(answer.answer, 3)
            elif str(question.answerType) == "Likert5":
                answerValue = calculate_value(answer.answer, 5)
            elif str(question.answerType) == "Likert5N":
                answerValue = calculate_reversed_value(answer.answer, 5)
            elif str(question.answerType) == "Likert7":
                answerValue = calculate_value(answer.answer, 7)
            elif str(question.answerType) == "Likert7N":
                answerValue = calculate_reversed_value(answer.answer, 7)
            elif str(question.answerType) == "Likert10":
                answerValue = calculate_value(answer.answer, 10)
            elif str(question.answerType) == "Likert10N":
                answerValue = calculate_reversed_value(answer.answer, 10)
            elif str(question.answerType) == "Time":
                answerValue = is_time_within_range(answer.answer, question.time_start, question.time_end)
            elif answer.answer == "null":
                answerValue = 0
            else:
                try:
                    answerValue = float(answer.answer)
                except (ValueError, TypeError):
                    answerValue = 0

            weight = question.weight if question.weight is not None else 1.0
            category_scores[str(category)] += float(answerValue) * weight
            category_weights[str(category)] += weight
            category_data[str(category)]["total_weight"] += weight
            category_data[str(category)]["questions"].append(
                {
                    "question": question.question,
                    "user_answer": answer.answer,
                    "question_type": question.answerType,
                    "min_value": question.min,
                    "max_value": question.max,
                    "time_start": question.time_start,
                    "time_end": question.time_end,
                }
            )
            category_data[str(category)]["id"] = category.id

    category_percentages = {
        k: round(((v / category_data[k]["total_weight"]) * 100), 2)
        for k, v in category_scores.items()
    }
    for category, data in category_data.items():
        data["score"] = category_scores[category]
        data["weight"] = category_weights[category]
        data["percentage"] = category_percentages.get(category, 0)

    combined_data = {
        category: {
            "id": data["id"],
            "percentage": data["percentage"],
            "score": data["score"],
            "weight": data["weight"],
            "questions": data["questions"],
        }
        for category, data in category_data.items()
    }

    return dict(category_percentages), combined_data

def calculate_category_score_percentage_for_audit(current_user_id):
    all_categories = Category.objects.all()
    category_data = defaultdict(
        lambda: {"id": None, "percentage": 0, "score": 0, "weight": 0, "total_weight": 0, "questions": []}
    )

    for category in all_categories:
        category_data[category] = {
            "id": category.id,
            "percentage": 0,
            "score": 0.0,
            "weight": 0.0,
            "total_weight": 0.0,
            "questions": [],
        }

    answers = UserAnswer.objects.filter(user_id=current_user_id)

    for answer in answers:
        question = answer.question
        category = question.category

        if category in category_data:
            if str(question.answerType) == "Range":
                answerValue = check_within_range(answer.answer, question.min, question.max)
            elif str(question.answerType) == "BoolP":
                answerValue = 0 if answer.answer == "False" else 1
            elif str(question.answerType) == "BoolN":
                answerValue = 0 if answer.answer == "True" else 1
            elif str(question.answerType) == "Likert3":
                answerValue = calculate_value(answer.answer, 3)
            elif str(question.answerType) == "Likert3N":
                answerValue = calculate_reversed_value(answer.answer, 3)
            elif str(question.answerType) == "Likert5":
                answerValue = calculate_value(answer.answer, 5)
            elif str(question.answerType) == "Likert5N":
                answerValue = calculate_reversed_value(answer.answer, 5)
            elif str(question.answerType) == "Likert7":
                answerValue = calculate_value(answer.answer, 7)
            elif str(question.answerType) == "Likert7N":
                answerValue = calculate_reversed_value(answer.answer, 7)
            elif str(question.answerType) == "Likert10":
                answerValue = calculate_value(answer.answer, 10)
            elif str(question.answerType) == "Likert10N":
                answerValue = calculate_reversed_value(answer.answer, 10)
            elif str(question.answerType) == "Time":
                answerValue = is_time_within_range(answer.answer, question.time_start, question.time_end)
            elif answer.answer == "null":
                answerValue = 0
            else:
                try:
                    answerValue = float(answer.answer)
                except (ValueError, TypeError):
                    answerValue = 0
            weight = question.weight if question.weight is not None else 1.0

            category_data[category]["score"] += answerValue * weight
            category_data[category]["weight"] += weight
            category_data[category]["total_weight"] += weight
            category_data[category]["questions"].append(
                {
                    "question": question.question,
                    "user_answer": answer.answer,
                    "question_type": question.answerType,
                    "min_value": question.min,
                    "max_value": question.max,
                    "time_start": question.time_start,
                    "time_end": question.time_end,
                }
            )
    for category, data in category_data.items():
        total_weight = data["total_weight"]
        data["percentage"] = round((data["score"] / total_weight) * 100, 2) if total_weight > 0 else 0

    combined_data = {
        category_id: {
            "id": data["id"],
            "percentage": data["percentage"],
            "score": data["score"],
            "weight": data["weight"],
            "questions": data["questions"],
        }
        for category_id, data in category_data.items()
    }
    
    return dict(category_data), combined_data
