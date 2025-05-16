from django.utils.deprecation import MiddlewareMixin
from django.core.cache import cache

class StoreUserInCacheMiddleware(MiddlewareMixin):
    def process_request(self, request):
        # Check if the user is authenticated
        if request.user.is_authenticated:
            # Store the user's ID in the cache
            print("User authenticated")
            cache.set('current_user', request.user.id, timeout=600)  # Cache for 10 minutes
        else:
            # If no authenticated user, set the cache to empty
            print("No authenticated user")
            cache.set('current_user', None, timeout=600)  # Cache for 10 minutes
