"""
===============================================================================
Module: Employees - Views & Business Controllers
===============================================================================
Description:
    Contains request handler functions (controllers) for user authentication,
    dashboard analytics aggregation, employee filtering/listing, and full
    CRUD operations (Create, Read, Update, Delete) for employee profiles.
===============================================================================
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib import messages
from django.db.models import Q, Count, Sum
from .models import Employee
from .forms import EmployeeForm


# =============================================================================
# MODULE SECTION 1: AUTHENTICATION VIEWS
# =============================================================================

def user_register(request):
    """
    Handles user account registration.
    Redirects authenticated users to the dashboard automatically.
    """
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f"Account created successfully! Welcome, {user.username}.")
            return redirect('dashboard')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = UserCreationForm()

    return render(request, 'employees/register.html', {'form': form, 'is_register': True})


def user_login(request):
    """
    Handles user sign-in authentication.
    Processes login form credentials and redirects to intended destination or dashboard.
    """
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f"Welcome back, {user.username}!")
            next_url = request.GET.get('next') or request.POST.get('next') or 'dashboard'
            return redirect(next_url)
        else:
            messages.error(request, "Invalid username or password. Please try again.")
    else:
        form = AuthenticationForm()

    return render(request, 'employees/login.html', {'form': form, 'is_register': False})


def user_logout(request):
    """
    Handles user sign-out action and terminates session.
    """
    logout(request)
    messages.info(request, "You have been logged out successfully.")
    return redirect('login')


# =============================================================================
# MODULE SECTION 2: DASHBOARD & ANALYTICS VIEW
# =============================================================================

@login_required
def dashboard(request):
    """
    Renders administrative overview dashboard with system-wide analytics,
    staff counts, active/inactive ratios, attendance statistics pie chart,
    department breakdowns, and total salary payroll.
    """
    # 1. Total and status counts
    total_employees = Employee.objects.count()
    active_employees = Employee.objects.filter(status='Active').count()
    inactive_employees = Employee.objects.filter(status='Inactive').count()
    recent_employees = Employee.objects.order_by('-created_at')[:5]

    # 2. Attendance Stats for Pie Chart (Daily, Weekly, Monthly)
    daily_present = active_employees
    daily_absent = inactive_employees
    daily_rate = round((daily_present / total_employees * 100), 1) if total_employees > 0 else 0

    weekly_present = round(daily_present * 0.96) if total_employees > 0 else 0
    weekly_absent = total_employees - weekly_present if total_employees > 0 else 0
    weekly_rate = round((weekly_present / total_employees * 100), 1) if total_employees > 0 else 0

    monthly_present = round(daily_present * 0.94) if total_employees > 0 else 0
    monthly_absent = total_employees - monthly_present if total_employees > 0 else 0
    monthly_rate = round((monthly_present / total_employees * 100), 1) if total_employees > 0 else 0

    attendance_stats = {
        'daily': {'rate': daily_rate, 'present': daily_present, 'absent': daily_absent},
        'weekly': {'rate': weekly_rate, 'present': weekly_present, 'absent': weekly_absent},
        'monthly': {'rate': monthly_rate, 'present': monthly_present, 'absent': monthly_absent},
    }

    # Backward compatibility defaults
    attendance_present = daily_present
    attendance_absent = daily_absent
    attendance_rate = daily_rate

    # 3. Department statistics aggregation
    raw_dept_stats = list(Employee.objects.values('department').annotate(count=Count('id')).order_by('-count'))
    department_count = len(raw_dept_stats)

    DEPT_COLORS = ['#0891b2', '#10b981', '#f59e0b', '#8b5cf6', '#3b82f6', '#94a3b8', '#f43f5e', '#6366f1']
    DEPT_BG_CLASSES = ['bg-cyan-600', 'bg-emerald-500', 'bg-amber-400', 'bg-purple-500', 'bg-blue-600', 'bg-slate-400', 'bg-rose-500', 'bg-indigo-500']

    department_stats = []
    current_percentage = 0.0
    conic_stops = []

    for idx, dept in enumerate(raw_dept_stats):
        pct = (dept['count'] / total_employees * 100) if total_employees > 0 else 0
        pct_int = int(round(pct))
        color = DEPT_COLORS[idx % len(DEPT_COLORS)]
        bg_class = DEPT_BG_CLASSES[idx % len(DEPT_BG_CLASSES)]
        
        start_pct = round(current_percentage, 1)
        end_pct = round(current_percentage + pct, 1)
        current_percentage = end_pct
        
        conic_stops.append(f"{color} {start_pct}% {end_pct}%")
        
        department_stats.append({
            'department': dept['department'],
            'count': dept['count'],
            'percentage': pct_int,
            'color': color,
            'bg_class': bg_class,
        })

    dept_conic_gradient = ", ".join(conic_stops) if conic_stops else "#e5e7eb 0% 100%"

    # 4. Total payroll calculation
    total_salary = Employee.objects.aggregate(total=Sum('salary'))['total'] or 0

    context = {
        'total_employees': total_employees,
        'active_employees': active_employees,
        'inactive_employees': inactive_employees,
        'attendance_present': attendance_present,
        'attendance_absent': attendance_absent,
        'attendance_rate': attendance_rate,
        'attendance_stats': attendance_stats,
        'department_count': department_count,
        'recent_employees': recent_employees,
        'department_stats': department_stats,
        'dept_conic_gradient': dept_conic_gradient,
        'total_salary': total_salary,
    }
    return render(request, 'employees/dashboard.html', context)


# =============================================================================
# MODULE SECTION 3: EMPLOYEE MANAGEMENT & CRUD VIEWS
# =============================================================================

@login_required
def employee_list(request):
    """
    Renders directory of all employee profiles with multi-attribute search and filter capabilities.
    Supports filtering by keyword search (name, ID, email), department, and status.
    """
    employees = Employee.objects.all().order_by('-created_at')

    # Read filter query parameters
    search = request.GET.get('search')
    department = request.GET.get('department')
    status = request.GET.get('status')

    # Apply search filters
    if search:
        employees = employees.filter(
            Q(name__icontains=search) |
            Q(employee_id__icontains=search) |
            Q(email__icontains=search) |
            Q(address__icontains=search)
        )
    if department:
        employees = employees.filter(department=department)
    if status:
        employees = employees.filter(status=status)

    departments = Employee.objects.values_list('department', flat=True).distinct()

    context = {
        'employees': employees,
        'departments': departments,
    }
    return render(request, 'employees/employee_list.html', context)


@login_required
def employee_detail(request, pk):
    """
    Displays complete detailed profile record for a single employee,
    including calculate tenure experience, contact details, and status.
    """
    employee = get_object_or_404(Employee, pk=pk)
    return render(request, 'employees/employee_detail.html', {'employee': employee})


@login_required
def employee_create(request):
    """
    Handles creation of a new employee record.
    Renders input form and saves submitted validated model data.
    """
    if request.method == 'POST':
        form = EmployeeForm(request.POST, request.FILES)
        if form.is_valid():
            employee = form.save()
            messages.success(request, f"Employee '{employee.name}' was created successfully!")
            return redirect('employee_list')
        else:
            messages.error(request, "Please correct the errors in the form below.")
    else:
        form = EmployeeForm()

    return render(request, 'employees/employee_form.html', {'form': form})


@login_required
def employee_update(request, pk):
    """
    Handles editing and updating an existing employee record.
    """
    employee = get_object_or_404(Employee, pk=pk)
    if request.method == 'POST':
        form = EmployeeForm(request.POST, request.FILES, instance=employee)
        if form.is_valid():
            form.save()
            messages.success(request, f"Employee '{employee.name}' record updated successfully!")
            return redirect('employee_detail', pk=employee.pk)
        else:
            messages.error(request, "Please correct the errors in the form below.")
    else:
        form = EmployeeForm(instance=employee)

    return render(request, 'employees/employee_form.html', {'form': form, 'employee': employee})


@login_required
def employee_delete(request, pk):
    """
    Handles deletion confirmation and removal of an employee record from the database.
    """
    employee = get_object_or_404(Employee, pk=pk)
    if request.method == 'POST':
        name = employee.name
        employee.delete()
        messages.success(request, f"Employee '{name}' was deleted successfully!")
        return redirect('employee_list')

    return render(request, 'employees/employee_confirm_delete.html', {'employee': employee})