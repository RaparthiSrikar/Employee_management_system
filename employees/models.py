"""
===============================================================================
Module: Employees - Data Models
===============================================================================
Description:
    Defines the database schema and business logic properties for the Employee
    Management System. Includes the Employee model, choice fields, and custom
    calculated properties such as work experience tenure calculation.
===============================================================================
"""

from django.db import models
from datetime import date


class Employee(models.Model):
    """
    Employee Model representing an individual staff member in the system.

    Attributes:
        employee_id (str): Unique identifier code assigned to the employee (e.g. EMP-1001).
        name (str): Full legal name of the employee.
        email (str): Primary corporate or personal email address (unique).
        phone (str): Contact phone number.
        department (str): Functional team or division within the organization.
        designation (str): Job title or role position.
        salary (Decimal): Monthly/annual compensation value.
        joining_date (Date): Official employment start date.
        gender (str): Gender choice selection (Male, Female, Other).
        image (Image): Optional profile photograph stored in media storage.
        status (str): Employment status flag (Active or Inactive).
        created_at (DateTime): Timestamp when the record was initially saved.
        updated_at (DateTime): Timestamp when the record was last modified.
    """

    # Choice Options for Selection Fields
    GENDER_CHOICES = [
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('Other', 'Other'),
    ]

    STATUS_CHOICES = [
        ('Active', 'Active'),
        ('Inactive', 'Inactive'),
    ]

    # Core Identification Fields
    employee_id = models.CharField(
        max_length=20,
        unique=True,
        help_text="Unique organizational employee registration number"
    )
    name = models.CharField(
        max_length=100,
        help_text="Full name of the employee"
    )
    email = models.EmailField(
        unique=True,
        help_text="Unique primary email address"
    )
    phone = models.CharField(
        max_length=15,
        help_text="Primary phone number"
    )
    address = models.TextField(
        blank=True,
        null=True,
        help_text="Primary physical or residential address"
    )

    # Organizational & Role Details
    department = models.CharField(
        max_length=100,
        help_text="Department or team division"
    )
    designation = models.CharField(
        max_length=100,
        help_text="Official job title"
    )
    salary = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Compensation amount"
    )
    joining_date = models.DateField(
        help_text="Date when employee joined the organization"
    )
    gender = models.CharField(
        max_length=10,
        choices=GENDER_CHOICES,
        help_text="Gender identity option"
    )

    # Media & Status Metadata
    image = models.ImageField(
        upload_to='employees/',
        blank=True,
        null=True,
        help_text="Profile image file upload"
    )
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='Active',
        help_text="Current employment status"
    )

    # Automatic Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def experience(self):
        """
        Calculates total experience tenure from joining_date to today's date.

        Returns:
            str: Human-readable string formatted as 'X yrs Y mos', 'Y mos', or '0 mos'.
        """
        if not self.joining_date:
            return "N/A"

        today = date.today()
        joining = self.joining_date

        # Handle future dates gracefully
        if joining > today:
            return "0 mos"

        # Calculate difference components
        years = today.year - joining.year
        months = today.month - joining.month
        days = today.day - joining.day

        # Adjust for negative day offset
        if days < 0:
            months -= 1
        # Adjust for negative month offset
        if months < 0:
            years -= 1
            months += 12

        # Format output string parts
        parts = []
        if years > 0:
            parts.append(f"{years} yr{'s' if years > 1 else ''}")
        if months > 0 or years == 0:
            parts.append(f"{months} mo{'s' if months != 1 else ''}")

        return " ".join(parts) if parts else "0 mos"

    def __str__(self):
        """String representation of the Employee object."""
        return f"{self.employee_id} - {self.name}"