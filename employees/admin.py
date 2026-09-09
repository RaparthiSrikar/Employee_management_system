"""
===============================================================================
Module: Employees - Django Admin Interface
===============================================================================
Description:
    Registers the Employee model with Django's administrative back-office portal.
    Configures display columns, search fields, and filter sidebars.
===============================================================================
"""

from django.contrib import admin
from .models import Employee


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    """
    Admin control configuration for Employee records.
    """

    # Table View Column Display Configuration
    list_display = (
        'employee_id',
        'name',
        'email',
        'department',
        'designation',
        'salary',
        'status',
    )

    # Search Bar Lookup Fields
    search_fields = (
        'employee_id',
        'name',
        'email',
        'department',
        'designation',
    )

    # Right Sidebar Filtering Options
    list_filter = (
        'department',
        'status',
        'gender',
    )