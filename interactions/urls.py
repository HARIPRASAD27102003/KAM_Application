from django.urls import path
from . import views

urlpatterns = [
    path('restaurant/<str:restaurant_name>/add_interaction/', views.add_interaction, name='add_interaction'),
    path('restaurant/<str:restaurant_name>/orders/', views.orders_page, name='orders_page'),
    path('restaurant/<str:restaurant_name>/interactions', views.interactions_page, name='interactions_page'),
    path('order/<str:order_id>/', views.order_details, name='order_details'),
    path('interaction/<int:interaction_id>/', views.interaction_detail, name='interaction_detail'),
]
# dfs
