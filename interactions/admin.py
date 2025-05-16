from django.contrib import admin
from .models import Interaction, Order,CallFrequency


@admin.register(Interaction)
class InteractionAdmin(admin.ModelAdmin):
    list_display = ('restaurant', 'contact','kam', 'interaction_type','date_time','notes','is_order_related','order')

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('restaurant', 'order_id', 'date_time','order_details', 'status')

@admin.register(CallFrequency)
class CallFrequencyAdmin(admin.ModelAdmin):
    list_display = ('restaurant','days_between_calls','last_call','next_call')