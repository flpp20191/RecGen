from django.conf import settings
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import (
    authenticate,
    login,
    logout,
    update_session_auth_hash,
    get_user_model,
)
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.contrib.auth.tokens import default_token_generator
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes, force_str
from django.core.mail import EmailMessage
from django.db.models import Q, Count
from accounts.models import *
from audit.models import *
from base.forms import *
from .forms import (
    CustomPasswordChangeForm,
    RegisterForm,
    SetNewPasswordForm,
    ResetPasswordEmailForm,
    UserForm,
)
import environ
env = environ.Env()
environ.Env.read_env()
User = get_user_model()

def login_user(request):
    """
    Handles user login by verifying the provided username and password.

    Parameters:
    - request: HttpRequest object that contains metadata about the request.

    Returns:
    - If the request method is POST and the login credentials are correct, the user is authenticated and redirected to the Dashboard.
    - If the request method is POST and the login credentials are incorrect, an error message is displayed, and the user is redirected back to the login page.
    - If the request method is GET (or any other method), the login page is rendered.
    """
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect("base:Dashboard")

        else:
            messages.error(request, "Username or password is incorrect.")
            return redirect("accounts:login")

    return render(request, "authenticate/login.html")


def logout_user(request):
    """
    Logs the user out and redirects them to the home page.

    This view handles the user logout process by calling Django's built-in logout function,
    which clears the session data and effectively logs out the user. After logging out,
    the user is redirected to the home page.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponseRedirect: A redirect to the 'login' URL.
    """
    logout(request)
    return redirect("accounts:login")


@login_required
def user_settings(request):
    """
    Handles the user settings page, allowing users to view and update their associated user information.

    This view requires the user to be logged in. If the user is not authenticated, it raises a 404 error.
    The view supports both GET and POST requests:
    - GET: Displays the current user information associated with the user.
    - POST: Allows the user to update their user information.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: Renders the 'user_settings.html' template with the user form and any relevant messages.
    """
    if not request.user.is_authenticated:
        raise Http404("User needs to be authenticated to access settings.")

    user, created = UserInformation.objects.get_or_create(user_information=request.user)

    user_form = UserForm(instance=user)
    submit_user_messages = []
    if request.method == "POST":
        user_form = UserForm(request.POST, instance=user)
        if user_form.is_valid():
            saved_user = user_form.save(commit=False)
            saved_user.user = request.user
            saved_user.save()

            submit_user_text_message = "Data was updated successfully."
            submit_user_messages.append({"text": submit_user_text_message, "tags": "success"})


    context = {
        "user": request.user,
        "user_information": user,
        "user_form": user_form,
        "submit_user_messages": submit_user_messages,
    }
    return render(request, "authenticate/user_settings.html", context)


def register(request):
    """
    Handles user registration.

    Parameters:
    - request: HttpRequest object that contains metadata about the request.

    Returns:
    - Renders the registration form on a GET request or if registration is disabled.
    - On a POST request, if the form is valid, the user is registered and redirected to the login page.
    - If the form is invalid, error messages are displayed, and the form is re-rendered with errors.
    """
    if not env('ALLOW_REGISTRATION'):
        return render(request, "authenticate/register_disabled.html")
    if request.method == "POST":
        form = RegisterForm(request.POST)  
        if form.is_valid():
            user = form.save()
            for category in Category.objects.all():
                UserCategory.objects.create(user=user, category=category)
            return redirect("accounts:login")  
        else:
            
            for field in form.errors:
                for error in form.errors[field]:
                    messages.error(request, error)
    else:
        form = RegisterForm()  
    return render(request, "authenticate/register.html", {"form": form})


@login_required
def password_change(request):
    """
    Handles password change and resetting user answers for selected categories.

    This view allows the logged-in user to perform two main actions:
    1. Change their password using a custom password change form.
    2. Reset (delete) their answers to questions within specific categories.

    If the user requests a password change, the form is validated, and if successful, 
    the password is updated and the session is re-authenticated to prevent logout.

    If the user requests to reset their answers for selected categories, 
    the selected categories are processed, and answers related to those categories are deleted.

    Args:
        request (HttpRequest): The HTTP request object, which contains data such as the form input 
        and the action to be performed.

    Returns:
        HttpResponse: The rendered 'password_change_form' template, 
        along with the form, categories with answers, and success/error messages.
    """
    other_messages = []
    password_messages = []
    current_user_id = request.user.id
    form = CustomPasswordChangeForm(request.user)  
    if request.method == "POST":
        action = request.POST.get("action", None)
        if action == "delete_answers":
            selected_category_ids = request.POST.getlist("categories_ids")
            if selected_category_ids:
                UserAnswer.objects.filter(
                    user=request.user, question__category_id__in=selected_category_ids
                ).delete()
                other_message_text = "Answers to selected categories were reset."
                other_messages.append({"text": other_message_text, "tags": "success"})
            else:
                other_message_text = "No categories were selected."
                other_messages.append({"text": other_message_text, "tags": "error"})
        elif action == "change_password":
            form = CustomPasswordChangeForm(request.user, request.POST)
            if form.is_valid():
                user = form.save()
                update_session_auth_hash(request, user)  
                password_change_message = "Your password was successfully updated!"
                password_messages.append({"text": password_change_message, "tags": "success"})
    categories = Category.objects.annotate(
        num_answers=Count("question__useranswer", filter=Q(question__useranswer__user=current_user_id))
    ).filter(num_answers__gt=0)

    return render(
        request,
        "authenticate/password_change_form.html",
        {
            "form": form, 
            "categories": categories, 
            "password_messages": password_messages, 
            "other_messages": other_messages,
        },
    )


def password_change_done(request):
    """
    Handles the rendering of the password change done page.

    This view is typically called after a user has successfully changed their password.
    It simply renders a confirmation page informing the user that their password has been changed.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: The rendered 'password_change_done' template.
    """
    return render(request, "authenticate/password_change_done.html")


def password_reset_request(request):
    """
    Handles requests to reset a user's password.

    Parameters:
    - request: HttpRequest object that contains metadata about the request.

    Returns:
    - Renders the password reset form if the request method is GET or if the form is invalid.
    - If the request method is POST and the form is valid, sends an email to the user with instructions to reset their password.
    """
    if request.method == "POST":
        password_reset_form = ResetPasswordEmailForm(request.POST)
        if password_reset_form.is_valid():
            data = password_reset_form.cleaned_data["email"]
            associated_users = User.objects.filter(Q(email=data))
            if associated_users.exists():
                subject = "Password Reset Requested"
                email_template_name = "authenticate/password_reset_email_en.txt"
                for user in associated_users:
                    c = {
                        "email": user.email,
                        "domain": env('DOMAIN_NAME'),
                        "site_name": env('PROJECT_NAME'),
                        "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                        "user": user,
                        "token": default_token_generator.make_token(user),
                        "protocol": "http"
                    }
                    email = render_to_string(email_template_name, c)
                    try:
                        msg = EmailMessage(
                            subject, email, env('PASSWORD_RESTORE_EMAIL'), [user.email]
                        )
                        msg.send()
                        messages.success(request, "Instructions for resetting your password have been sent to your email.")

                    except Exception as e:
                        messages.error(request, f"Email sending error: {str(e)}")
            else:
                messages.error(request, "No user registered with this email address.")
        else:
            messages.error(request, "Please correct the errors below.")

    password_reset_form = ResetPasswordEmailForm()
    return render(request, "authenticate/password_reset_form.html", {
        "password_reset_form": password_reset_form,
    })


def password_reset_done(request):
    """
    Handles the rendering of the password reset done page.

    This view is typically called after a user has successfully requested a password reset.
    It simply renders a confirmation page informing the user that an email has been sent
    with further instructions on how to reset their password.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: The rendered 'password_reset_done' template.
    """
    return render(
        request, "authenticate/password_reset_done.html"
    )


def password_reset_confirm(request, uidb64, token):
    """
    Handles the password reset confirmation process.

    This view is triggered when a user clicks on the password reset link sent to their email.
    It verifies the user's identity using the encoded user ID (uidb64) and token, then allows 
    the user to set a new password if the verification is successful.

    Args:
        request (HttpRequest): The HTTP request object.
        uidb64 (str): The base64 encoded user ID.
        token (str): The password reset token.

    Returns:
        HttpResponse: 
            - If the user ID and token are valid and the request method is POST:
                - Renders the password reset form for the user to set a new password.
            - If the user ID and token are invalid or the request method is GET:
                - Renders the 'password_reset_invalid' template.
            - If the form is valid on POST:
                - Redirects the user to the 'password_reset_complete' page after saving the new password.
    """
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is None or not default_token_generator.check_token(user, token):
        return render(
            request, 
            "authenticate/password_reset_invalid.html",
            context,
        )
    if request.method == "POST":
        form = SetNewPasswordForm(user=user, data=request.POST)
        if form.is_valid():
            form.save()
            return redirect("password_reset_complete")
    else:
        form = SetNewPasswordForm(user=user)

    context = {
        "form": form,
        "uid": uidb64,
        "token": token,
    }

    return render(
        request,
        "authenticate/password_reset_confirm.html",
        context,
    )

    
def password_reset_complete(request):
    """
    Handles the rendering of the password reset complete page.

    This view is typically called after a user has successfully reset their password.
    It simply renders a confirmation page informing the user that their password has been reset
    and that they can now log in with their new credentials.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: The rendered 'password_reset_complete' template.
    """
    return render(request, "authenticate/password_reset_complete.html")

