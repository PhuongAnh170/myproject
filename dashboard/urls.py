from django.urls import path
from dashboard import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.dashboard_overview, name='overview'),
    path('delivery/', views.dashboard_delivery, name='delivery'),
    path('api/metric-data/', views.api_metric_data, name='api_metric_data'),
    path('api/delivery-data/', views.api_delivery_data, name='api_delivery_data'),
]