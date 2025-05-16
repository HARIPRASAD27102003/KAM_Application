from django.db import models
from django.conf import settings
from datetime import datetime, timedelta, timezone  
from django.utils.timezone import now
import pytz
from dateutil.relativedelta import relativedelta
from profiles.models import Contact, Restaurant,KAM
from django.db import connection

class Order(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Success', 'Success'),
        ('Cancelled', 'Cancelled'),
    ]

    restaurant = models.ForeignKey(
        Restaurant,
        on_delete=models.CASCADE,
        related_name='orders',
        help_text="The restaurant associated with this order"
    )
    order_id = models.CharField(
        max_length=255,
        unique=True,
        null=True,
        help_text="Unique identifier for the order"
    )
    date_time = models.DateTimeField(
        null=True, 
        help_text="Date and time of the order"
    )
    order_details = models.TextField(help_text="Details of the order")
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='Pending',
        help_text="The current status of the order"
    )

    def __str__(self):
        return f"Order {self.order_id} ({self.status})"


class Interaction(models.Model):
    TYPE_CHOICES = [
        ('Call', 'Call'),
        ('Email', 'Email'),
        ('Meeting', 'Meeting'),
    ]

    restaurant = models.ForeignKey(
        Restaurant,
        on_delete=models.CASCADE,
        related_name='interactions',
        help_text="The restaurant this interaction is related to"
    )
    contact = models.ForeignKey(
        Contact,
        on_delete=models.CASCADE,
        related_name='interactions',
        help_text="The contact person involved in the interaction"
    )
    kam = models.ForeignKey(
        KAM,
        on_delete=models.CASCADE,
        related_name='interactions',
        null=True,
        help_text="The KAM (Key Account Manager) responsible for this interaction"
    )
    interaction_type = models.CharField(
        max_length=20,
        help_text="Type of interaction"
    )
    date_time = models.DateTimeField(
        null=True,
        unique=True,
        help_text="Date and time of the interaction"
    )
    notes = models.TextField(
        null=True,
        blank=True,
        help_text="Additional notes about the interaction"
    )
    is_order_related = models.BooleanField(
        default=False,
        help_text="Indicates if this interaction is related to an order"
    )
    order = models.ForeignKey(
        Order,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='interactions',
        help_text="The order associated with this interaction (if applicable)"
    )

    def __str__(self):
        return f"{self.interaction_type} with {self.restaurant.name}"


class CallFrequency(models.Model):
    restaurant = models.OneToOneField(
        Restaurant,
        on_delete=models.CASCADE,
        related_name='call_frequencies',
        help_text="The restaurant this call frequency is associated with"
    )
    days_between_calls = models.PositiveIntegerField(
        help_text="Number of days after which a call should be made"
    )
    last_call = models.DateTimeField(
        null=True,
        blank=True,
        help_text="The last time a call was made"
    )
    next_call = models.DateTimeField(
        help_text="The next scheduled call",
        default=now,
    )
    next_call_list = models.JSONField(
        default=list,
        help_text="List of (next_call, order_id) pairs"
    )

    def save(self, *args, **kwargs):
        """Override save to handle the last_call and next_call."""
        try:
            # Set last_call to now if not provided
            if not self.last_call:
                self.last_call = now()

            # Calculate the next_call time based on last_call and days_between_calls
            if self.days_between_calls is not None:
                self.next_call = self.last_call + timedelta(days=self.days_between_calls)

            # Call the superclass save method to persist the instance
            super().save(*args, **kwargs)

        except Exception as e:
            print(f"Error in save: {e}")
            
            
   