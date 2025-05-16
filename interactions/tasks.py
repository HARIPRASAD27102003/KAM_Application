from celery import shared_task
from django.core.cache import cache
from datetime import date, datetime
from interactions.models import CallFrequency,Order
from profiles.models import KAM,Restaurant
from django.contrib.auth import get_user_model
import pytz


User = get_user_model()

@shared_task 
def schedule_calls():
    # print("hhh")
    
    # Retrieve the current user from the cache
    user_id = cache.get('current_user')
    if not user_id:
        print("No authenticated user found in cache. Stopping the process.")
        cache.set('today_calls', [], timeout=60 * 60)  # Cache an empty list if no calls
        return  # Stop the task if no user is in the cache
    
    try:
        user = User.objects.get(id=user_id)
        # print(user)
    except User.DoesNotExist:
        print(f"User with ID {user_id} does not exist. Stopping the process.")
        return  # Stop the task if the user does not exist in the database

    try:
        kam = KAM.objects.get(email=user)
        print(kam)
    except KAM.DoesNotExist:
        print(f"No KAM found for user {user}. Stopping the process.")
        return  # Stop the task if no KAM is associated with the user

    # Get the KAM's timezone or default to UTC
    kam_timezone = kam.timezone or 'UTC'
    # print(kam_timezone)
    try:
        kam_tz = pytz.timezone(kam_timezone)
    except pytz.UnknownTimeZoneError:
        print(f"Invalid timezone: {kam_timezone}, falling back to UTC.")
        kam_tz = pytz.UTC

    # Get today's date in the KAM's timezone
    today = datetime.now(kam_tz).date()
    # print(today)

    # Filter restaurants with the current KAM aidojhaiosd
    restaurants_with_kam = Restaurant.objects.filter(kam=kam)
    calls_data = CallFrequency.objects.filter(restaurant__in=restaurants_with_kam)
    print(calls_data)

    calls_today = []
    for call in calls_data:
        # Check if the restaurant's kam matches the user (this depends on your data structure)
        if call.restaurant.kam == user:
            next_call = call.next_call
            
            # Check if next_call is a string (ISO format)
            if isinstance(next_call, str):
                # If it's a string, we need to convert it to a datetime object
                next_call = datetime.fromisoformat(next_call)  # Parse ISO format to datetime
                
                # If the datetime is naive (no timezone), we assume it's in UTC
                if next_call.tzinfo is None:
                    next_call = pytz.UTC.localize(next_call)
            elif isinstance(next_call, datetime):
                # If it's already a datetime object, check if it's naive and convert it to UTC if necessary
                if next_call.tzinfo is None:
                    next_call = pytz.UTC.localize(next_call)
            
            # Convert the next_call to kam_tz
            next_call_kam_time = next_call.astimezone(kam_tz)

            # Debugging output
            # print("Next Call (in Kam timezone):", next_call_kam_time)
            # print("Today's date:", today)

            # Check if the date part of next_call matches today's date
            if next_call_kam_time.date() == today:
                calls_today.append(call)

# Now calls_today contains all the calls where next_call is today in Kam timezone
    
    if calls_today:
        cache.set('today_calls', list(calls_today), timeout=60 * 60)  # Cache for 1 hour
        print(f"Cached calls for today: {calls_today}")
    else:
        print("No calls to schedule today.")
        cache.set('today_calls', [], timeout=60 * 60)  # Cache an empty list if no calls

        

@shared_task
def calculate_all_restaurants_performance():
    # Fetch all restaurants
    restaurants = Restaurant.objects.all()

    # Calculate performance for each restaurant
    performance_scores = {}
    for restaurant in restaurants:
        performance_score = calculate_performance(restaurant)
        performance_scores[restaurant.id] = performance_score

    # Store the performance scores in the cache
    cache.set('restaurant_performance_scores', performance_scores, timeout=60 * 60)  # Cache for 1 hour

    return performance_scores


def calculate_performance(restaurant):
    # Get the total number of orders and their statuses
    total_orders = Order.objects.filter(restaurant=restaurant).count()
    successful_orders = Order.objects.filter(restaurant=restaurant, status='completed').count()
    success_rate = (successful_orders / total_orders) * 100 if total_orders > 0 else 0

    # Calculate interaction frequency
    total_interactions = restaurant.interactions.count()
    interaction_frequency = total_interactions / 30  # Assuming monthly interaction frequency

    # Initialize performance score with success rate and interaction frequency
    performance_score = (success_rate * 0.4 + interaction_frequency * 0.3)

    # Check if the restaurant is new and add 40 points
    if restaurant.status == 'New':
        performance_score += 40  # Add 40 points for new restaurants
    
    performance_score = round(performance_score, 2)

    return performance_score