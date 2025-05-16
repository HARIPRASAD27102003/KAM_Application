from datetime import timedelta
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.utils import timezone
from dateutil.relativedelta import relativedelta
from interactions.tasks import schedule_calls
from .models import Restaurant, Order, Interaction, Contact, CallFrequency
from django.contrib import messages
from django.utils.timezone import now
from django.contrib.auth.decorators import login_required

@login_required
def interaction_detail(request, interaction_id):
    # Get the specific interaction using its ID
    print(interaction_id)
    interaction = get_object_or_404(Interaction, id=interaction_id)
    
    # Get related interactions for the same order, if the interaction is order-related
    related_interactions = None
    if interaction.is_order_related and interaction.order:
        related_interactions = Interaction.objects.filter(order=interaction.order).exclude(id=interaction.id)

    return render(request, 'interaction_details.html', {
        'interaction': interaction,
        'related_interactions': related_interactions
    })


@login_required
def orders_page(request, restaurant_name):
    restaurant = Restaurant.objects.get(name=restaurant_name)
    orders = Order.objects.filter(restaurant=restaurant)
    print(orders)
    return render(request, 'orders.html', {'restaurant': restaurant, 'orders': orders})
@login_required
def interactions_page(request, restaurant_name):
    restaurant = Restaurant.objects.get(name=restaurant_name)
    interactions = Interaction.objects.filter(restaurant=restaurant).order_by('-date_time')
    return render(request, 'interactions.html', {'restaurant': restaurant, 'interactions': interactions})

@login_required
def order_details(request, order_id):
    print(f"Accessing order with ID: {order_id}") # Debugging output
    print("hhh")
    order = get_object_or_404(Order, order_id=order_id)
    interactions = order.interactions.all()
    
    return render(request, 'order_details.html', {
        'order': order,
        'interactions': interactions
    })

@login_required
def add_interaction(request, restaurant_name):
    try:
        # Fetch the restaurant by name
        restaurant = Restaurant.objects.get(name=restaurant_name)
    except Restaurant.DoesNotExist:
        messages.error(request, 'Restaurant not found')
        return redirect('restaurants_page')

    try:
        # Fetch orders associated with the restaurant
        orders = Order.objects.filter(restaurant=restaurant, status__iexact='Pending')

    except Exception as e:
        messages.error(request, f"Error fetching orders: {str(e)}")
        orders = []

    try:
        # Fetch all contacts (KAMs) associated with the restaurant
        contacts = Contact.objects.filter(restaurant=restaurant)
    except Exception as e:
        messages.error(request, f"Error fetching contacts: {str(e)}")
        contacts = []

    if request.method == "POST":
        try:
            # Fetch data from the form
            interaction_type = request.POST.get('interaction_type')
            notes = request.POST.get('notes')
            order_option = request.POST.get('order_option')
            contact_name = request.POST.get('contact')
            related_to_order = request.POST.get('related_to_order')
            print(related_to_order)
            # Determine if the interaction is related to an order
            is_order_related = (related_to_order == 'yes')
            print(is_order_related)

            order_count = Order.objects.filter(restaurant=restaurant).count() + 1

            if order_count > 1:
                restaurant.status = 'Active'
            elif order_count == 1:
                restaurant.status = 'New'
            else:
                restaurant.status = 'Inactive'
            restaurant.save()

            # Retrieve the contact instance based on the selected contact name
            contact = contacts.filter(name=contact_name).first()
            if not contact:
                raise ValueError('Contact not found')

            # Handle existing orders or new orders based on the user selection
            if is_order_related:
                  # Handle existing orders
                if order_option == "existing_order":
                    order_id = request.POST.get('order_id')
                    try:
                        # Retrieve the existing order
                        order = Order.objects.get(order_id=order_id)
                        order.order_details = request.POST.get('order_details')
                        order.status = request.POST.get('order_status')
                        # print(order.status)
                        order.save()
                        print("now")
                        # Update CallFrequency
                        try:
                            # Get the CallFrequency instance for the restaurant
                            call_frequency = CallFrequency.objects.get(restaurant=restaurant)

                            # Calculate the next_call_date using days_between_calls
                            days = request.POST.get('next_interaction_days')
                            print(f"Using {days} days from CallFrequency for the calculation.")
                            days = int(days)
                            current_date = now()
                            print(f"Current date: {current_date}")
                            
                            next_call_date = current_date + relativedelta(days=days)
                            print(f"Calculated next_call_date: {next_call_date}")

                            # Initialize next_call_list if it doesn't exist
                            if not call_frequency.next_call_list:
                                call_frequency.next_call_list = []

                            # Add the new interaction
                            order_found = False
                            for entry in call_frequency.next_call_list:
                                if entry.get('order_id') == order_id:
                                    # If order_id exists, update the next_call
                                    entry['next_call'] = next_call_date.isoformat()
                                    print(entry['next_call'])
                                    if order.status=='Success':
                                        entry['order_id']=""
                                    order_found = True
                                    break
                            print(order_found)
                            # If the order_id doesn't exist, append a new entry
                            if not order_found:
                                call_frequency.next_call_list.append({
                                    "next_call": next_call_date.isoformat(),  # Ensure datetime is serialized as a string
                                    "order_id": order_id
                                })
                            
                            print(f"Updated next_call_list: {call_frequency.next_call_list}")

                            # Now calculate the next_call based on last_call and days_between_calls
                            call_frequency.last_call = now()
                            if not call_frequency.last_call:
                                call_frequency.last_call = current_date  # Set last_call to now if it's None

                            calculated_next_call = call_frequency.last_call + timedelta(days=days)
                            print(f"Calculated next_call: {calculated_next_call}")

                            # Update the next_call to the earlier of the calculated_next_call or the existing one
                            if call_frequency.next_call:
                                call_frequency.next_call = min(calculated_next_call, call_frequency.next_call)
                            else:
                                call_frequency.next_call = calculated_next_call

                            # Save the updated fields to the database
                            call_frequency.days_between_calls = days  # Ensure days_between_calls is updated
                            call_frequency.save(update_fields=['next_call_list', 'next_call', 'days_between_calls'])

                            print("Successfully added interaction and updated CallFrequency object.")
                        except ValueError as ve:
                            print(f"ValueError: {str(ve)}")
                        except Exception as e:
                            print(f"Error in update_call_frequency: {str(e)}")
                        # Save the interaction
                        interaction = Interaction(
                            restaurant=restaurant,
                            contact=contact,
                            kam=restaurant.kam,
                            interaction_type=interaction_type,
                            date_time=now(),
                            notes=notes,
                            is_order_related=True,
                            order=order
                        )
                        # print(interaction)
                        interaction.save()
                        schedule_calls().delay()
                        messages.success(request, 'Interaction added successfully with existing order.')
                        return redirect('interactions_page', restaurant_name=restaurant_name)
                    except Order.DoesNotExist:
                        raise ValueError('Order not found')

                # Handle new orders
                elif order_option == "new_order":
                    order_details = request.POST.get('order_details2')
                    new_order_id = f"ORD-{timezone.now().strftime('%Y%m%d%H%M%S')}"
                    new_order = Order(
                        restaurant=restaurant,
                        order_id=new_order_id,
                        date_time=now(),
                        order_details=order_details,
                        status='Pending'
                    )
                    new_order.save()

                    try:
                        # Get the CallFrequency instance for the restaurant
                        call_frequency = CallFrequency.objects.get(restaurant=restaurant)

                        # Calculate the next_call_date using days_between_calls
                        days = request.POST.get('next_interaction_days')
                        print(f"Using {days} days from CallFrequency for the calculation.")
                        days = int(days)
                        current_date = now()
                        print(f"Current date: {current_date}")
                        
                        next_call_date = current_date + relativedelta(days=days)
                        print(f"Calculated next_call_date: {next_call_date}")

                        # Initialize next_call_list if it doesn't exist
                        if not call_frequency.next_call_list:
                            call_frequency.next_call_list = []

                        # Add the new interaction
                        call_frequency.next_call_list.append({
                            "next_call": next_call_date.isoformat(),  # Ensure datetime is serialized as a string
                            "order_id": new_order_id
                        })
                        call_frequency.last_call = now()
                        print(f"Updated next_call_list: {call_frequency.next_call_list}")

                        # Now calculate the next_call based on last_call and days_between_calls
                        if not call_frequency.last_call:
                            call_frequency.last_call = current_date  # Set last_call to now if it's None

                        calculated_next_call = call_frequency.last_call + timedelta(days=days)
                        print(f"Calculated next_call: {calculated_next_call}")

                        # Update the next_call to the earlier of the calculated_next_call or the existing one
                        if call_frequency.next_call:
                            call_frequency.next_call = min(calculated_next_call, call_frequency.next_call)
                        else:
                            call_frequency.next_call = calculated_next_call

                        # Save the updated fields to the database
                        call_frequency.days_between_calls = days  # Ensure days_between_calls is updated
                        call_frequency.save(update_fields=['next_call_list', 'next_call', 'days_between_calls'])

                        print("Successfully added interaction and updated CallFrequency object.")

                    except ValueError as ve:
                        print(f"ValueError: {str(ve)}")
                    except Exception as e:
                        print(f"Error in update_call_frequency: {str(e)}")
                    call_frequency.save()
                    # Save the interaction
                    interaction = Interaction(
                        restaurant=restaurant,
                        contact=contact,
                        kam=restaurant.kam,
                        interaction_type=interaction_type,
                        date_time=now(),
                        notes=notes,
                        is_order_related=True,
                        order=new_order
                    )
                    interaction.save()
                    schedule_calls().delay()

                    messages.success(request, 'Interaction added successfully with new order.')
                    return redirect('interactions_page', restaurant_name=restaurant_name)
            
        except ValueError as ve:
                messages.error(request, str(ve))
        except Exception as e:
                messages.error(request, f"An unexpected error occurred: {str(e)}")
            

    # For GET requests, render the form page with the restaurant, orders, and contacts
    return render(request, 'step1.html', {'restaurant': restaurant, 'orders': orders, 'contacts': contacts})

