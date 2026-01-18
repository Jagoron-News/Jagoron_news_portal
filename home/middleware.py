"""
Middleware for URL Redirection
"""
from django.shortcuts import redirect
from django.http import HttpResponsePermanentRedirect, HttpResponseRedirect
from home.models import URLRedirection


class URLRedirectionMiddleware:
    """
    Middleware to handle URL redirections
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Check for URL redirection before processing the request
        path = request.path
        
        # Try to find an active redirection
        try:
            redirection = URLRedirection.objects.filter(
                old_url=path,
                is_active=True
            ).first()
            
            if redirection:
                # Determine redirect type
                if redirection.redirect_type == '301':
                    return HttpResponsePermanentRedirect(redirection.new_url)
                else:  # 302
                    return HttpResponseRedirect(redirection.new_url)
        except Exception:
            # If there's any error (e.g., database not ready), just continue
            pass
        
        response = self.get_response(request)
        return response
