from django import template
import pytz
from datetime import datetime

register = template.Library()

@register.filter
def convert_timezone(value, target_timezone):
    """
    Convert the given datetime (value) to the target timezone.
    :param value: datetime in UTC
    :param target_timezone: Target timezone string (e.g., "Asia/Kolkata")
    :return: datetime in the target timezone
    """
    if not value or not target_timezone:
        return value  # Return original value if missing
    
    try:
        utc_timezone = pytz.utc
        target_tz = pytz.timezone(target_timezone)
        value = value.replace(tzinfo=utc_timezone)  # Ensure UTC timezone is set
        return value.astimezone(target_tz).strftime("%Y-%m-%d %H:%M:%S")  # Format as desired
    except Exception as e:
        return value  # Fallback to original value on error
