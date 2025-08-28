from collections import defaultdict
import time
from django.conf import settings
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import redirect, render, get_object_or_404
from django.views import View
import pandas as pd
from requests import request
from base.calculation_script import calculate_category_score_percentage, calculate_score_percentage, calculate_category_score_percentage_for_audit
from audit.models import *
from accounts.models import *
from formtools.wizard.views import SessionWizardView
from .forms import CategoryForm, InputDataImportForm, QuestionForm, RecommendationForm, WizardPage1
from django.db import models
from datetime import datetime
import datetime as dt
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils import translation
from django.urls import reverse, reverse_lazy
from django.contrib.auth.models import User
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.utils.decorators import method_decorator
from django.contrib import messages
import logging
import os
import environ
env = environ.Env()
environ.Env.read_env()

class UserWizardView(LoginRequiredMixin, SessionWizardView):

    form_list = [WizardPage1]
    template_name = "audit/dataWizard.html"

    def get_context_data(self, form, **kwargs):
        context = super().get_context_data(form=form, **kwargs)
        instance_id = self.kwargs.get("pk")
        category = get_object_or_404(Category, id=instance_id)
        context["category"] = category
        return context

    def get_form_kwargs(self, step=None):
        kwargs = super().get_form_kwargs(step)
        instance_id = self.kwargs.get("pk", None)
        user = self.request.user

        if step == "0":
            kwargs.update({
                "pk": instance_id,
                "user": user,
            })
        else:
            kwargs.update({

            })
        return kwargs

    def post(self, *args, **kwargs):
        form = self.get_form(data=self.request.POST, files=self.request.FILES)
        if form.is_valid():
            self.storage.set_step_data(self.steps.current, self.process_step(form))
            if self.steps.next:
                self.storage.current_step = self.steps.next
            else:
                return self.render_done(form, **kwargs)
        else:
            print("Form errors:", form.errors)
        return self.render(form)

    def done(self, form_list, **kwargs):
        user = self.request.user
        category_id = self.kwargs.get("pk")
        category = get_object_or_404(Category, id=category_id)

        for form in form_list:
            for question_text, answer in form.cleaned_data.items():
                if answer is None:
                    answer = "null"
                elif isinstance(answer, dt.time):
                    answer = answer.strftime("%H:%M")
                question = get_object_or_404(Question, question=question_text, category=category)
                UserAnswer.objects.update_or_create(
                    user=user, question=question, defaults={"answer": answer}
                )
        return redirect("base:Dashboard")

@login_required
def audits(request):
    all_categories = Category.objects.filter(parent=None)
    current_user_id = request.user.id
    user, user_created = UserInformation.objects.get_or_create(user_information=request.user)
    if user_created:
        user.save()

    _, category_data = calculate_category_score_percentage_for_audit(current_user_id)

    for category in all_categories:
        category_has_questions = category.question_set.exists()
        category_has_recommendations = category.recommendation_set.exists()

        if category in category_data:
            if category_has_questions and category_has_recommendations:
                category_data[category]['has_questions_or_recommendations'] = True
            else:
                category_data[category]['has_questions_or_recommendations'] = False
                print(f"{category} has no questions and no recommendations.")

    user_category_tracking = {uc.category.id: uc.is_tracking for uc in UserCategory.objects.filter(user=request.user)}
    context = {
        "user": request.user,
        "categories": all_categories,
        "current_user_id": current_user_id,
        "category_data": category_data,
        "user_category_tracking": user_category_tracking,
    }
    return render(request, "audit/audits.html", context)

@login_required
def recommendation_view(request):
    Recommendation_thershold = int(env("RECOMMENDATION_THRESHOLD"))
    clicked_recommendation = request.COOKIES.get("clickedRecommendation", 0)
    clickedRecommendationTrue = request.COOKIES.get(
        "clickedRecommendationTrue", "false"
    )

    has_accepted_cookies_client = (
        request.COOKIES.get("has_accepted_cookies", "false") == "true"
    )
    user = request.user
    current_user_id = request.user.id
    (
        answers,
        recommendation_list_tier_one_true,
        recommendation_list_tier_two_true,
        recommendation_list_tier_three_true,
        recommendation_data,
    ) = calculate_score_percentage(current_user_id)


    all_percentages_100 = all(
        data["percentage"] == 100 for data in recommendation_data.values()
    )
    filtered_recommendations = {
        recommendation: data
        for recommendation, data in recommendation_data.items()
        if data["percentage"] <= Recommendation_thershold
    }
    context = {
        "answers": answers,
        "recommendation_data": filtered_recommendations,
        "all_percentages_100": all_percentages_100,
        "clicked_recommendation": clicked_recommendation,
        "has_accepted_cookies_client": has_accepted_cookies_client,
        "clickedRecommendationTrue": clickedRecommendationTrue,
    }

    return render(request, "audit/recommendations.html", context)

@method_decorator(login_required, name="dispatch")
class UpdateTrackingStatusView(View):
    def post(self, request, *args, **kwargs):
        category_id = request.POST.get("category_id")
        is_tracking = request.POST.get("is_tracking") == "true"

        try:
            category = Category.objects.get(pk=category_id)
        except Category.DoesNotExist as e:
            raise Http404("category does not exist.") from e

        UserCategory.objects.update_or_create(
            user=request.user, category=category, defaults={"is_tracking": is_tracking}
        )

        return JsonResponse({"status": "ok"})

@login_required
def categories(request):
    user = request.user
    current_user_id = request.user.id
    user_categories = request.user.categories.filter(parent=None) 
    category_data = defaultdict(dict) 
    questions = Question.objects.all()

    for category in user_categories:
        recommendations = Recommendation.objects.filter(categories=category)
        category_data[category.id]['recommendations'] = recommendations
        category_data[category.id]['children'] = list(category.children.all())

    category_percentage, category_data_percentage = calculate_category_score_percentage(current_user_id)
    
    context = {
        "categories": user_categories,
        "category_data": category_data,
        "category_percentage": category_percentage,
        "category_data_percentage": category_data_percentage,
    }

    return render(request, "audit/categories.html", context)


# CRUD for categories
class CategoryListView(ListView):
    model = Category
    template_name = 'audit/category_list.html'

class CategoryCreateView(CreateView):
    model = Category
    form_class = CategoryForm
    template_name = 'audit/category_form.html'
    success_url = reverse_lazy('audit:category-list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        previous_url = self.request.GET.get('previous_url', self.request.META.get('HTTP_REFERER'))
        context['previous_url'] = previous_url
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        previous_url = self.request.POST.get('previous_url', '')
        if previous_url:
            return HttpResponseRedirect(previous_url)
        else:
            return HttpResponseRedirect(self.success_url)
        
class CategoryUpdateView(UpdateView):
    model = Category
    form_class = CategoryForm
    template_name = 'audit/category_form.html'
    success_url = reverse_lazy('audit:category-list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        previous_url = self.request.GET.get('previous_url', self.request.META.get('HTTP_REFERER'))
        context['previous_url'] = previous_url
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        previous_url = self.request.POST.get('previous_url', '')
        if previous_url:
            return HttpResponseRedirect(previous_url)
        else:
            return HttpResponseRedirect(self.success_url)

class CategoryDeleteView(DeleteView):
    model = Category
    template_name = 'audit/category_confirm_delete.html'
    success_url = reverse_lazy('audit:category-list')
    def delete(self, request, *args, **kwargs):
        category = self.get_object()
        UserCategory.objects.filter(category=category).delete()
        return super().delete(request, *args, **kwargs)

# CRUD for Recommendations
class RecommendationListView(ListView):
    model = Recommendation
    template_name = 'audit/recommendation_list.html'

class RecommendationCreateView(CreateView):
    model = Recommendation
    form_class = RecommendationForm
    template_name = 'audit/recommendation_form.html'
    success_url = reverse_lazy('audit:recommendation-list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        previous_url = self.request.GET.get('previous_url', self.request.META.get('HTTP_REFERER'))
        context['previous_url'] = previous_url
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        previous_url = self.request.POST.get('previous_url', '')
        if previous_url:
            return HttpResponseRedirect(previous_url)
        else:
            return HttpResponseRedirect(self.success_url)

    def form_invalid(self, form):
        messages.error(self.request, "There was an error saving the recommendation. Please check the form fields.")
        return render(self.request, self.template_name, self.get_context_data(form=form))

class RecommendationUpdateView(UpdateView):
    model = Recommendation
    form_class = RecommendationForm  
    template_name = 'audit/recommendation_form.html'
    success_url = reverse_lazy('audit:recommendation-list')  

    def form_valid(self, form):
        response = super().form_valid(form)
        previous_url = self.request.POST.get('previous_url', '')
        if previous_url:
            return HttpResponseRedirect(previous_url)
        else:
            return HttpResponseRedirect(self.success_url)

class RecommendationDeleteView(DeleteView):
    model = Recommendation
    template_name = 'audit/recommendation_confirm_delete.html'  
    success_url = reverse_lazy('audit:recommendation-list')  

# CRUD for Questions
class QuestionListView(ListView):
    model = Question
    template_name = 'audit/question_list.html'

class QuestionCreateView(CreateView):
    model = Question
    form_class = QuestionForm
    template_name = 'audit/question_form.html'
    success_url = reverse_lazy('audit:question-list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        previous_url = self.request.META.get('HTTP_REFERER')
        context['previous_url'] = previous_url
        return context

    def form_valid(self, form):
        if form.is_valid():
            self.object = form.save()
            messages.success(self.request, "Question successfully created.")
            return super().form_valid(form)
        else:
            messages.error(self.request, "There was an error creating the question. Please check your input.")
            return self.form_invalid(form)

class QuestionUpdateView(UpdateView):
    model = Question
    form_class = QuestionForm
    template_name = 'audit/question_form.html'
    success_url = reverse_lazy('audit:question-list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        previous_url = self.request.META.get('HTTP_REFERER')
        context['previous_url'] = previous_url
        return context

    def form_valid(self, form):
        original_question = Question.objects.get(pk=self.object.pk)
        
        if form.is_valid():
            self.object = form.save(commit=False)

            if original_question.answerType != self.object.answerType:
                category = original_question.category

                related_questions = Question.objects.filter(category=category)
                UserAnswer.objects.filter(question__in=related_questions).delete()
                messages.success(self.request, "Answers to related questions have been reset due to question type change.")


            self.object.save()
            form.save_m2m()  
            messages.success(self.request, "Question successfully updated.")
            previous_url = self.request.POST.get('previous_url', '')
            if previous_url:
                return HttpResponseRedirect(previous_url)
            else:
                return HttpResponseRedirect(self.success_url)
        else:
            messages.error(self.request, "There was an error updating the question. Please check your input.")
            return self.form_invalid(form)

class QuestionDeleteView(DeleteView):
    model = Question
    template_name = 'audit/question_confirm_delete.html'
    success_url = reverse_lazy('audit:question-list')


# Data input from Excel file
def upload_data_input_excel(request):
    if request.method == 'POST':
        form = InputDataImportForm(request.POST, request.FILES)
        if form.is_valid():
            excel_file = request.FILES['file']
            try:
                xls = pd.ExcelFile(excel_file)

                insert_categories(xls)
                print("Categories inserted successfully.")
                category_errors = validate_categories(xls)

                insert_recommendations(xls)
                print("Recommendations inserted successfully.")
                recommendation_errors = validate_recommendations(xls)

                insert_questions(xls)
                print("Questions inserted successfully.")
                question_errors = validate_questions(xls)

                if category_errors or recommendation_errors or question_errors:
                    messages.error(request, "Validation errors detected!")
                    messages.error(request, "\n".join(category_errors + recommendation_errors + question_errors))
                else:
                    insert_question_recommendation_links(xls)  
                    insert_categories_recommendation_links(xls)  
                    messages.success(request, 'Data imported successfully!')
                    return redirect('base:Dashboard')
            except Exception as e:
                messages.error(request, f"Error processing file: {str(e)}")
    else:
        form = InputDataImportForm()

    return render(request, 'audit/input_data_upload.html', {'form': form})


def insert_categories(xls):
    df = xls.parse('Category')
    for index, row in df.iterrows():
        try:
            # print(f"Processing Category Row {index + 1}: {row}")
            
            category, created = Category.objects.update_or_create(
                name=row['Name'],
                defaults={'description': row['Description'] if pd.notna(row['Description']) else ''}
            )
            
            if created:
                print(f"Category '{category.name}' created.")
            else:
                print(f"Category '{category.name}' updated.")
            
            if pd.notna(row['Parent Categories']):
                # print(f"Processing Parent Categories for row {index + 1}: {row['Parent Categories']}")
                parent_names = row['Parent Categories'].split(',')
                parent_categories = Category.objects.filter(name__in=parent_names)
                category.parent.set(parent_categories)
                # print(f"Parent categories set for Category '{category.name}'")
        except Exception as e:
            print(f"Error processing Category Row {index + 1}: {e}")
            raise


def insert_recommendations(xls):
    df = xls.parse('Recommendation')
    for index, row in df.iterrows():
        try:
        #     print(f"Processing Recommendation Row {index + 1}: {row}")
            
            recommendation, created = Recommendation.objects.update_or_create(
                recommendation=row['Recommendation'],
                defaults={'weight': row['Weight']}
            )
            text = row['Recommendation']
            # print(repr(text), len(text))
            if created:
                print(f"Recommendation '{recommendation.recommendation}' created.")
            else:
                print(f"Recommendation '{recommendation.recommendation}' updated.")
            
        except Exception as e:
            print(f"Error processing Recommendation Row {index + 1}: {e}")
            raise


def insert_questions(xls):
    df = xls.parse('Question')
    for index, row in df.iterrows():
        try:
            # print(f"Processing Question Row {index + 1}: {row}")
            categories = Category.objects.filter(name=row['Category'])
            
            if categories.count() == 0:
                raise Exception(f"Category '{row['Category']}' does not exist.")
            elif categories.count() > 1:
                raise Exception(f"Multiple categories found for '{row['Category']}'. Please ensure categories are unique.")
            
            category = categories.first()
            question_type = Question_type.objects.get(type=row['Question_type'])
            
            question, created = Question.objects.update_or_create(
                question=row['Question'],
                defaults={
                    'category': category,
                    'answerType': question_type,
                    'min': row['min'] if pd.notna(row['min']) else None,
                    'max': row['max'] if pd.notna(row['max']) else None,
                    'time_start': row['time_start'] if pd.notna(row['time_start']) else None,
                    'time_end': row['time_end'] if pd.notna(row['time_end']) else None,
                    'weight': row['weight'] if pd.notna(row['weight']) else 1,
                    'description': row['description'] if pd.notna(row['description']) else ''
                }
            )
            
            if created:
                print(f"Question '{question.question}' created.")
            else:
                print(f"Question '{question.question}' updated.")
        except Question_type.DoesNotExist:
            print(f"Error: Question_type '{row['Question_type']}' not found in the database.")
            raise
        except Exception as e:
            print(f"Error processing Question Row {index + 1}: {e}")
            raise


def insert_question_recommendation_links(xls):
    df = xls.parse('RecommendationQuestion')
    for index, row in df.iterrows():
        try:
            questions = Question.objects.filter(question=row['Question'])
            if questions.count() == 0:
                raise Exception(f"Question '{row['Question']}' does not exist.")
            
            rec_texts = row['Recommendation'].split(';')
            recommendations = Recommendation.objects.filter(recommendation__in=rec_texts)

            for question in questions:
                question.recommendations.add(*recommendations)
                print(f"Recommendations added for Question '{question.question}'")
        except Question.DoesNotExist:
            print(f"Error: Question '{row['Question']}' not found in the database.")
            raise
        except Exception as e:
            print(f"Error processing Recommendation-Question Connection Row {index + 1}: {e}")
            raise


def insert_categories_recommendation_links(xls):
    df = xls.parse('RecommendationCategories')
    for index, row in df.iterrows():
        try:
            # print(f"Processing Recommendation-Categories Connection Row {index + 1}: {row}")

            recommendations = Recommendation.objects.filter(recommendation = row['Recommendation'])
            if recommendations.count() == 0:
                raise Exception(f"Recomemndations  '{row['Recommendation']}' does not exist.")
            
            categories = Category.objects.filter(name = row['Category'])
            for recommendation in recommendations:
                recommendation.categories.add(*categories)
                # print(f"Recommendations added for Question '{recommendation.categories}'")
        except Question.DoesNotExist:
            print(f"Error: Question '{row['Question']}' not found in the database.")
            raise
        except Exception as e:
            print(f"Error processing Recommendation-Question Connection Row {index + 1}: {e}")
            raise


def validate_categories(xls):
    df = xls.parse('Category')
    errors = []
    
    for index, row in df.iterrows():
        try:
            # print(f"Validating Category Row {index + 1}: {row}")
            if not row['Name']:
                errors.append(f"Row {index + 1}: Category name is missing.")
            if pd.notna(row['Parent Categories']):
                # print(f"Checking Parent Categories for row {index + 1}: {row['Parent Categories']}")
                parent_names = row['Parent Categories'].split(',')
                invalid_parents = [name for name in parent_names if not Category.objects.filter(name=name).exists()]
                if invalid_parents:
                    errors.append(f"Row {index + 1}: Parent category '{', '.join(invalid_parents)}' does not exist.")
        except Exception as e:
            print(f"Error in Category validation at row {index + 1}: {e}")
    return errors


def validate_recommendations(xls):
    df = xls.parse('Recommendation')
    errors = []
    for index, row in df.iterrows():
        try:
            # print(f"Validating Recommendation Row {index + 1}: {row}")
            if not row['Recommendation']:
                errors.append(f"Row {index + 1}: Recommendation text is missing.")
        except Exception as e:
            print(f"Error in Recommendation validation at row {index + 1}: {e}")
    return errors


def validate_questions(xls):
    df = xls.parse('Question')
    errors = []
    for index, row in df.iterrows():
        try:
            if not row['Question']:
                errors.append(f"Row {index + 1}: Question text is missing.")
            if not Category.objects.filter(name=row['Category']).exists():
                errors.append(f"Row {index + 1}: Category '{row['Category']}' does not exist.")
            if row['Question_type'] and not Question_type.objects.filter(type=row['Question_type']).exists():
                errors.append(f"Row {index + 1}: Question type ID '{row['Question_type']}' is invalid.")
            if pd.notna(row['recommendations']):
                print(f"Checking Recommendations for row {index + 1}: {row['recommendations']}")
                rec_texts = row['recommendations'].split(',')
                invalid_recommendations = [rec for rec in rec_texts if not Recommendation.objects.filter(recommendation=rec).exists()]
                if invalid_recommendations:
                    errors.append(f"Row {index + 1}: Recommendation(s) '{', '.join(invalid_recommendations)}' do not exist.")
        except Exception as e:
            print(f"Error in Question validation at row {index + 1}: {e}")
    return errors


def download_template(request, filename):
    file_path = os.path.join(settings.MEDIA_ROOT, filename)
    if os.path.exists(file_path):
        with open(file_path, 'rb') as file:
            response = HttpResponse(file.read(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            response['Content-Disposition'] = f'attachment; filename={filename}'
            return response
    else:
        raise Http404("File not found")