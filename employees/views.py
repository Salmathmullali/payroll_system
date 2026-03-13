from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import logout as django_logout
from django.contrib.auth.decorators import login_required
from .models import Employee, MonthlySalary 
from django.db.models import Q # Import your new model here

# ... (home, dashboard, logout_view, employee_form remain the same) ...
def home(request):
    # If user is already logged in, take them to dashboard
    if request.user.is_authenticated:
        return redirect('login')
    # Otherwise, take them to the login page
    return redirect('dashboard')


@login_required
def dashboard(request):
    search_query = request.GET.get('search')
    
    if search_query:
        # Search by Name OR Employee ID
        all_employees = Employee.objects.filter(
            Q(name__icontains=search_query) | 
            Q(emp_id__icontains=search_query)
        )
    else:
        all_employees = Employee.objects.all()

    return render(request, 'employees/dashboard.html', {
        'all_employees': all_employees
    })

def employee_list(request):
    search_query = request.GET.get('search')
    
    if search_query:
        # 1. Filter the database
        results = Employee.objects.filter(
            Q(name__icontains=search_query) | Q(emp_id__icontains=search_query)
        )
        
        # 2. AUTO-REDIRECT LOGIC:
        # If we found exactly 1 person, skip the list and go straight to their detail page
        if results.count() == 1:
            return redirect('employee_detail', pk=results.first().pk)
        
        all_employees = results
    else:
        all_employees = Employee.objects.all()
    
    return render(request, 'employees/dashboard.html', {'all_employees': all_employees})

def logout_view(request):

    django_logout(request)

    return redirect('login')



@login_required
def employee_form(request, pk=None):
    if pk:
        employee = get_object_or_404(Employee, pk=pk)
    else:
        employee = None

    if request.method == "POST":
        # Capture all the new percentage fields
        data = {
            'name': request.POST['name'],
            'designation': request.POST['designation'],
            'emp_id': request.POST['emp_id'],
            'email': request.POST['email'],
            'phone': request.POST['phone'],
            'address': request.POST['address'],
            'basic_salary': request.POST['basic_salary'],
            'da_percent': request.POST.get('da_percent', 50),
            'hra_percent': request.POST.get('hra_percent', 40),
            'other_percent': request.POST.get('other_percent', 10),
            'pf_percent': request.POST.get('pf_percent', 12),
            'esi_percent': request.POST.get('esi_percent', 0.75),
        }

        if employee:
            for key, value in data.items():
                setattr(employee, key, value)
            employee.save()
        else:
            Employee.objects.create(**data)
            
        return redirect('dashboard')

    return render(request, 'employees/employee_form.html', {
        'employee': employee, 
        'all_employees': Employee.objects.all()
    })

def payslip(request, pk):

    emp = get_object_or_404(Employee, pk=pk)

    context = {'emp': emp, 'payroll': emp.get_payroll_details()}

    return render(request, 'employees/payslip.html', context)

@login_required
def process_monthly_salary(request, emp_id):
    employee = get_object_or_404(Employee, id=emp_id)
    
    if request.method == "POST":
        # We only take the Month, Year, and Leaves from the user.
        # The model logic (save method) will handle all percentages automatically!
        salary_record = MonthlySalary.objects.create(
            employee=employee,
            month=request.POST.get('month'),
            year=request.POST.get('year'),
            leaves_taken=int(request.POST.get('leaves', 0)),
            manual_mode=request.POST.get('manual_mode') == 'on',
            custom_earnings=float(request.POST.get('custom_earnings', 0) or 0),
            custom_deductions=float(request.POST.get('custom_deductions', 0) or 0)
            # da, hra, pf, esi are REMOVED here. They will be calculated in models.py
        )
        return redirect('monthly_payslip', pk=salary_record.pk)

    return render(request, 'employees/salary_process_form.html', {'employee': employee})

def monthly_payslip(request, pk):
    salary = get_object_or_404(MonthlySalary, pk=pk)
    return render(request, 'employees/monthly_payslip_view.html', {
        'salary': salary,
        'all_employees': Employee.objects.all() # This fixes the navbar dropdown!
    })
@login_required
def employee_detail(request, pk):
    employee = get_object_or_404(Employee, pk=pk)
    # Get the latest 5 salary records for this employee
    salary_history = employee.salaries.all().order_by('-year', '-month') 
    return render(request, 'employees/employee_detail.html', {
        'employee': employee,
        'salary_history': salary_history
    })

@login_required
def edit_monthly_salary(request, pk):
    record = get_object_or_404(MonthlySalary, pk=pk)
    if request.method == "POST":
        record.leaves_taken = int(request.POST.get('leaves', 0))
        record.manual_mode = request.POST.get('manual_mode') == 'on'
        record.custom_earnings = float(request.POST.get('custom_earnings', 0) or 0)
        record.custom_deductions = float(request.POST.get('custom_deductions', 0) or 0)
        record.save() # The model logic will re-calculate everything
        return redirect('employee_detail', pk=record.employee.pk)

    return render(request, 'employees/edit_monthly_salary.html', {'record': record})
@login_required
def global_monthly_process(request):
    # This view allows selecting ANY employee from a dropdown
    employees = Employee.objects.all()
    
    if request.method == "POST":
        emp_id = request.POST.get('employee_id')
        employee = get_object_or_404(Employee, id=emp_id)
        
        salary_record = MonthlySalary.objects.create(
            employee=employee,
            month=request.POST.get('month'),
            year=request.POST.get('year'),
            leaves_taken=int(request.POST.get('leaves', 0)),
            manual_mode=request.POST.get('manual_mode') == 'on',
            custom_earnings=float(request.POST.get('custom_earnings', 0) or 0),
            custom_deductions=float(request.POST.get('custom_deductions', 0) or 0)
        )
        # Note: Your Model's save() method handles the DA/HRA/PF/ESI calculations automatically now!
        return redirect('monthly_payslip', pk=salary_record.pk)

    return render(request, 'employees/global_monthly_process.html', {'employees': employees})
def emp_full_list(request):
    employees = Employee.objects.all()
    return render(request, 'employees/employee_list.html', {'employees': employees})