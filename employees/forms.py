"""
===============================================================================
Module: Employees - Forms & UI Input Validation
===============================================================================
Description:
    Provides Django ModelForm definitions for managing Employee model data.
    Configures HTML input widget attributes, CSS Tailwind styling classes,
    placeholder texts, and custom field validation clean methods.
===============================================================================
"""

from django import forms
from .models import Employee


class EmployeeForm(forms.ModelForm):
    """
    ModelForm for creating and updating Employee instances.

    Includes custom field styling matching the clean solid light theme UI
    (white input backgrounds, dark text, gray borders, indigo focus rings).
    """

    class Meta:
        model = Employee
        fields = [
            'employee_id',
            'name',
            'email',
            'phone',
            'address',
            'department',
            'designation',
            'salary',
            'joining_date',
            'gender',
            'image',
            'status',
        ]
        
        # Shared Widget Styling CSS Classes
        input_css = (
            'w-full py-2.5 px-3.5 bg-white border border-gray-300 rounded-xl '
            'text-black text-sm placeholder-gray-400 focus:outline-none '
            'focus:border-indigo-600 focus:ring-1 focus:ring-indigo-600 transition-colors'
        )
        select_css = (
            'w-full py-2.5 px-3.5 bg-white border border-gray-300 rounded-xl '
            'text-black text-sm focus:outline-none focus:border-indigo-600 '
            'focus:ring-1 focus:ring-indigo-600 transition-colors'
        )

        widgets = {
            'employee_id': forms.TextInput(attrs={
                'class': input_css,
                'placeholder': 'e.g. EMP-1001',
            }),
            'name': forms.TextInput(attrs={
                'class': input_css,
                'placeholder': 'e.g. John Doe',
            }),
            'email': forms.EmailInput(attrs={
                'class': input_css,
                'placeholder': 'john.doe@company.com',
            }),
            'phone': forms.TextInput(attrs={
                'class': input_css,
                'placeholder': '+1 (555) 000-0000',
            }),
            'address': forms.Textarea(attrs={
                'class': input_css + ' h-20 resize-y',
                'placeholder': 'Enter full street address, city, state, postal code...',
                'rows': 3,
            }),
            'department': forms.TextInput(attrs={
                'class': input_css,
                'placeholder': 'e.g. Engineering, HR, Sales',
            }),
            'designation': forms.TextInput(attrs={
                'class': input_css,
                'placeholder': 'e.g. Senior Software Engineer',
            }),
            'salary': forms.NumberInput(attrs={
                'class': input_css,
                'placeholder': '75000.00',
                'step': '0.01',
            }),
            'joining_date': forms.DateInput(attrs={
                'class': input_css,
                'type': 'date',
            }),
            'gender': forms.Select(attrs={
                'class': select_css,
            }),
            'image': forms.FileInput(attrs={
                'class': (
                    'block w-full text-xs text-gray-500 file:mr-4 file:py-2.5 '
                    'file:px-4 file:rounded-xl file:border-0 file:text-xs '
                    'file:font-semibold file:bg-indigo-50 file:text-indigo-700 '
                    'hover:file:bg-indigo-100 file:cursor-pointer bg-white '
                    'border border-gray-300 rounded-xl'
                ),
                'accept': 'image/*',
            }),
            'status': forms.Select(attrs={
                'class': select_css,
            }),
        }

    def clean_salary(self):
        """
        Validates that salary is a non-negative decimal value.
        """
        salary = self.cleaned_data.get('salary')
        if salary is not None and salary < 0:
            raise forms.ValidationError("Salary cannot be a negative value.")
        return salary
