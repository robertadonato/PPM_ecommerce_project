from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    path('', views.OrderListView.as_view(), name='order_list'),
    path('history/', views.order_history, name='order_history'),
    path('create/', views.create_order, name='create_order'),
    
    path('manage/', views.manage_orders, name='manage_orders'),
    path('manage/<int:order_id>/', views.manage_order_detail, name='manage_order_detail'),
    path('manage/<int:order_id>/update-status/', views.update_order_status, name='update_order_status'),

    path('<str:order_number>/', views.OrderDetailView.as_view(), name='order_detail'),
]