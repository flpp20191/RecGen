# context_processors.py

from django.urls import resolve, Resolver404

def view_name(request):
    try:
        resolver_match = resolve(request.path_info)
        return {
            "view_name": resolver_match.view_name
        }
    except Resolver404:
        # Return an empty context or handle 404 situations gracefully
        return {}
    except Exception:
        # Catch any unexpected issues that might occur during lookup
        return {}
