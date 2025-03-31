import zoneinfo
from django.utils import timezone


class TimezoneMiddleware:
    """Middleware to set the active timezone based on user preferences."""
    
    def __init__(self, get_response):
        self.get_response = get_response
        
    def __call__(self, request):
        if request.user.is_authenticated:
            try:
                # Get the user's preferred timezone from their profile
                tz = request.user.timezone
                # Set the current timezone using zoneinfo
                timezone.activate(zoneinfo.ZoneInfo(tz))
            except (AttributeError, zoneinfo.ZoneInfoNotFoundError):
                # If there's any issue, fall back to UTC
                timezone.activate(zoneinfo.ZoneInfo('UTC'))
        else:
            # For unauthenticated users, use UTC
            timezone.activate(zoneinfo.ZoneInfo('UTC'))
            
        return self.get_response(request) 