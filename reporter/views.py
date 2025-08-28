import json
import matplotlib
import numpy as np
matplotlib.use('Agg') 

from operator import itemgetter
from django.shortcuts import render
from base.calculation_script import (
    calculate_score_percentage,
    calculate_category_score_percentage,
)
from audit.models import *
from accounts.models import *
import os
import uuid
from django.conf import settings
from django.utils import timezone
from django.http import HttpResponse, JsonResponse
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph, Table, TableStyle, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib import colors
from django.views.decorators.csrf import csrf_exempt
from django.contrib.staticfiles import finders
import matplotlib.pyplot as plt

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

@csrf_exempt
def generate_overall_report(request):
    current_user_id = request.user.id

    # Validate user information
    try:
        user_info = UserInformation.objects.get(user_information=current_user_id)
    except UserInformation.DoesNotExist:
        user_info = None

    # Validate user answers
    user_answers = UserAnswer.objects.filter(user=current_user_id).select_related('question')
    if not user_answers.exists():
        return HttpResponse("No data available to generate the report.", content_type="text/plain")

    # Calculate scores and validate data
    (
        answers,
        recommendation_list_tier_one_true,
        recommendation_list_tier_two_true,
        recommendation_list_tier_three_true,
        recommendation_data,
    ) = calculate_score_percentage(current_user_id)

    if not answers:
        return HttpResponse("No data available to generate the report.", content_type="text/plain")

    category, category_data = calculate_category_score_percentage(current_user_id)
    if not category_data:
        return HttpResponse("No data available to generate the report.", content_type="text/plain")

    sorted_categories = sorted(category.items(), key=itemgetter(1))
    average_value = sum(answers.values()) / len(answers) if answers else 0

    # Generate image only if average_value is valid
    image_path = None
    if average_value > 0:
        image_dir = os.path.join(settings.MEDIA_ROOT, "tempFiles")
        os.makedirs(image_dir, exist_ok=True)
        image_name = f"graph_{uuid.uuid4().hex}.png"
        image_path = os.path.join(image_dir, image_name)

        try:
            fig, ax = plt.subplots(figsize=(6, 1.5))
            ax.barh(
                ['Completion'],
                [average_value],
                color=['#198754' if average_value >= 66 else '#ffc107' if average_value >= 33 else '#dc3545']
            )
            ax.set_xlim(0, 100)
            ax.set_title('Compliance level')
            ax.get_yaxis().set_visible(False)
            plt.savefig(image_path, bbox_inches='tight')
            plt.close(fig)
        except Exception as e:
            print(f"Error while saving the image: {str(e)}")
            image_path = None

    # Prepare context
    context = {
        "user_info": user_info,
        "answers": answers,
        "recommendation_data": recommendation_data,
        "sorted_categories": sorted_categories,
        "category_data": category_data,
        "user_answers": user_answers, 
        "image_path": image_path,
    }

    # Generate PDF
    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = 'attachment; filename="report.pdf"'
    p = canvas.Canvas(response, pagesize=A4)
    draw_overall_report(p, context)
    p.showPage()
    p.save()

    # Clean up the image file
    if image_path and os.path.exists(image_path):
        os.remove(image_path)
    return response


def draw_overall_report(canvas, context):
    user_info = context.get("user_info")
    image_path = context.get("image_path")
    y_position = 750
    page_width, page_height = A4

    # Register fonts
    deja_vu_sans_path = finders.find('ttf/DejaVuSans.ttf')
    deja_vu_sans_bold_path = finders.find('ttf/DejaVuSans-Bold.ttf')
    pdfmetrics.registerFont(TTFont("DejaVuSans", deja_vu_sans_path))
    pdfmetrics.registerFont(TTFont("DejaVuSans-Bold", deja_vu_sans_bold_path))

    # Draw header
    canvas.setFont("DejaVuSans-Bold", 15)
    canvas.drawString(50, y_position, "Audit Result Report")
    y_position -= 30

    # Draw user information
    canvas.setFont("DejaVuSans", 12)
    if user_info:
        canvas.drawString(50, y_position, f"Name: {user_info.name or user_info.user_information.get_full_name()}")
        y_position -= 20
        canvas.drawString(50, y_position, f"Address: {user_info.address or 'N/A'}")
        y_position -= 20
        canvas.drawString(50, y_position, f"Contact Number: {user_info.contact_number or 'N/A'}")
        y_position -= 20
        canvas.drawString(50, y_position, f"Email: {user_info.contact_email or 'N/A'}")
    else:
        canvas.drawString(50, y_position, "No additional user information available.")
    y_position -= 40

    # Draw image if available
    if image_path and os.path.exists(image_path):
        canvas.drawImage(image_path, 300, y_position + 30, width=250, height=100)

    # Recommendations Score Section
    canvas.setFont("DejaVuSans-Bold", 14)
    canvas.drawString(50, y_position, "Recommendations Score")
    y_position -= 30

    if not context["answers"]:
        canvas.setFont("DejaVuSans", 12)
        canvas.drawString(50, y_position, "No recommendations available.")
        y_position -= 20
    else:
        custom_style = ParagraphStyle("Custom", fontName="DejaVuSans", fontSize=12, leading=15)
        data = [["No.", "Recommendation", "Score (%)"]]
        for idx, (recommendation, score) in enumerate(context["answers"].items(), start=1):
            recommendation_text = Paragraph(recommendation, custom_style)
            data.append([idx, recommendation_text, f"{score}%"])

        recommendation_table = Table(data, colWidths=[30, 400, 70])
        style_table(recommendation_table)
        y_position = render_table(canvas, recommendation_table, y_position, 750)

    # Audit Evaluation Section
    canvas.setFont("DejaVuSans-Bold", 14)
    canvas.drawString(50, y_position, "Audit Evaluation")
    y_position -= 30

    if not context["category_data"]:
        canvas.setFont("DejaVuSans", 12)
        canvas.drawString(50, y_position, "No category data available.")
        y_position -= 20
    else:
        category_data = [["No.", "Category", "Score (%)"]]
        for idx, (category, details) in enumerate(context["category_data"].items(), start=1):
            category_text = Paragraph(category, custom_style)
            percentage = details.get("percentage", 0)
            category_data.append([idx, category_text, f"{percentage}%"])

        category_table = Table(category_data, colWidths=[30, 400, 70])
        style_table(category_table)
        y_position = render_table(canvas, category_table, y_position, page_height)

    # User Answers Section
    canvas.setFont("DejaVuSans-Bold", 14)
    canvas.drawString(50, y_position, "User Answers")
    y_position -= 30

    if not context["user_answers"]:
        canvas.setFont("DejaVuSans", 12)
        canvas.drawString(50, y_position, "No user answers available.")
        y_position -= 20
    else:
        answer_data = [["No.", "Question", "Answer"]]
        for idx, answer in enumerate(context["user_answers"], start=1):
            question_text = Paragraph(answer.question.question, custom_style)
            mapped_answer = get_likert_value(answer.answer, answer.question.answerType.type)
            user_answer = mapped_answer if mapped_answer else "No answer"
            answer_data.append([idx, question_text, user_answer])

        answer_table = Table(answer_data, colWidths=[30, 350, 120])  
        style_table(answer_table)
        render_table(canvas, answer_table, y_position, page_height)


def style_table(table):
    # Apply table style
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'DejaVuSans-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('VALIGN', (1, 0), (-1, -1), 'MIDDLE'),
    ]))


def render_table(canvas, table, y_position, page_height):
    table.wrapOn(canvas, 500, y_position)  # Ensure the table is only 500 units wide
    table_height = table._height
    if y_position - table_height < 50:
        canvas.showPage()
        y_position = page_height - 50
    table.drawOn(canvas, 50, y_position - table_height)
    return y_position - table_height - 30

def get_likert_value(answer, answer_type):
    if answer_type == "Likert3":
        return dict(LAKERTA3_MAP_EN).get(int(answer), answer)
    elif answer_type == "Likert3N":
        return dict(LAKERTA3N_MAP_EN).get(int(answer), answer)
    elif answer_type == "Likert5":
        return dict(LAKERTA5_MAP_EN).get(int(answer), answer)
    elif answer_type == "Likert5N":
        return dict(LAKERTA5N_MAP_EN).get(int(answer), answer)
    elif answer_type == "Likert7":
        return dict(LAKERTA7_MAP_EN).get(int(answer), answer)
    elif answer_type == "Likert7N":
        return dict(LAKERTA7N_MAP_EN).get(int(answer), answer)
    elif answer_type == "Likert10":
        return dict(LAKERTA10_MAP_EN).get(int(answer), answer)
    elif answer_type == "Likert10N":
        return dict(LAKERTA10N_MAP_EN).get(int(answer), answer)
    return answer  # Default, if no mapping exists

def create_donut_chart(percentage, save_path):
    fig, ax = plt.subplots(figsize=(2, 2), subplot_kw=dict(aspect="equal"))

    # Define the sizes for the donut chart
    sizes = [percentage, 100 - percentage]
    colors = ['#198754', '#e9ecef']  # Green for progress, grey for remaining

    wedges, texts = ax.pie(sizes, colors=colors, startangle=90, wedgeprops=dict(width=0.3))

    # Add the percentage label in the middle
    ax.text(0, 0, f"{percentage}%", ha='center', va='center', fontsize=14, weight='bold')

    plt.savefig(save_path, bbox_inches='tight')
    plt.close(fig)

def create_gauge_chart(percentage, save_path):
    fig, ax = plt.subplots(figsize=(3, 3), subplot_kw={'projection': 'polar'})

    # Setting the theta range from 0 to 180 degrees
    theta = np.linspace(0, np.pi, 100)
    
    # Normalizing the percentage to the angle range
    r = np.ones_like(theta)
    
    # Plot the gauge background
    ax.fill_between(theta, 0, r, color='lightgrey')

    # Plot the gauge progress
    ax.fill_between(theta[:int(percentage)], 0, r[:int(percentage)], color='#198754')

    # Remove the polar grid and set aspect ratio
    ax.grid(False)
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_aspect(1)

    # Add percentage text in the center
    ax.text(0, 0, f"{percentage}%", ha='center', va='center', fontsize=16, weight='bold')

    plt.savefig(save_path, bbox_inches='tight')
    plt.close(fig)