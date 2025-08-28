from django.shortcuts import render
from django.urls import reverse
from accounts.models import *
from django.utils.deprecation import MiddlewareMixin
from django.utils import translation
from root import settings

class EnsureUserInformationMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            try:
                # Check if UserInformation exists, create if it doesn't
                user_information, created = UserInformation.objects.get_or_create(
                    user_information=request.user
                )
                if created:
                    print(f"UserInformation created for {request.user}")
            except Exception as e:
                print(f"Error occurred while checking/creating UserInformation: {e}")

        response = self.get_response(request)
        return response



class AdminSiteRestrictionMiddleware:
    """
    Middleware to restrict access to the admin site for non-superuser users.
    Args:
        get_response: The callable to get the response for the request.
    Explanation:
        The AdminSiteRestrictionMiddleware class is responsible for checking if a request is for the admin site and if the user is not a superuser. If these conditions are met, it returns a 403 Forbidden response with an error template. Otherwise, it allows the request to proceed.
    Returns:
        The response for the request.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        ADMIN_PATH = "/admin"

        # Process the request first (including authentication)
        response = self.get_response(request)

        if request.path.startswith(ADMIN_PATH) and not request.user.is_superuser:
            return render(request, "error/admin_page_restriction.html", status=403)

        return response


class PermissionsPolicyMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        response["Permissions-Policy"] = "geolocation=(), microphone=()"
        return response


class SimpleMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        # One-time configuration and initialization.

    def __call__(self, request):
        response = self.get_response(request)
        response.headers["Server"] = "None of your beeswax!"
        return response


class XContentTypeOptionsMiddleware(MiddlewareMixin):
    def process_response(self, request, response):
        response['X-Content-Type-Options'] = 'nosniff'
        return response