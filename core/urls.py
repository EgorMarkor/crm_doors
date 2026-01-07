from django.contrib.auth import views as auth_views
from django.urls import path

from core import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('login/', auth_views.LoginView.as_view(template_name='core/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('requests/installations/', views.installation_requests, name='installation_requests'),
    path('requests/deliveries/', views.delivery_requests, name='delivery_requests'),
    path('requests/installations/free/', views.free_installation_requests, name='free_installation_requests'),
    path('requests/deliveries/free/', views.free_delivery_requests, name='free_delivery_requests'),
    path('requests/installations/<int:request_id>/claim/', views.claim_installation, name='claim_installation'),
    path('requests/deliveries/<int:request_id>/claim/', views.claim_delivery, name='claim_delivery'),
    path('section/<slug:section>/', views.placeholder_section, name='placeholder_section'),
]
