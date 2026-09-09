"""
===============================================================================
Module: Employees - URL Routing Configuration
===============================================================================
Description:
    Maps URL paths to their corresponding view handlers within the employees app.
    Defines named routes for dashboard analytics, employee directory listing,
    CRUD actions (Create, Read, Update, Delete), and user authentication.
===============================================================================
"""

from django.urls import path
from . import views

urlpatterns = [
    # Dashboard Analytics View Route
    path('', views.dashboard, name='dashboard'),

    # Employee Directory & CRUD View Routes
    path('employees/', views.employee_list, name='employee_list'),
    path('employees/add/', views.employee_create, name='employee_create'),
    path('employees/<int:pk>/', views.employee_detail, name='employee_detail'),
    path('employees/<int:pk>/edit/', views.employee_update, name='employee_update'),
    path('employees/<int:pk>/delete/', views.employee_delete, name='employee_delete'),
    
    # User Authentication & Session View Routes
    path('register/', views.user_register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
]
