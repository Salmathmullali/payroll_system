from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import logout as django_logout
from django.contrib.auth.decorators import login_required
from .models import Employee, MonthlySalary # Import your new model here

# ... (home, dashboard, logout_view, employee_form remain the same) ...
def home(request):
    # If user is already logged in, take them to dashboard
    if request.user.is_authenticated:
        return redirect('login')
    # Otherwise, take them to the login page
    return redirect('dashboard')


@login_required
def dashboard(request):
    # We call it 'all_employees' so the navbar dropdown can see it
    employees = Employee.objects.all()
    return render(request, 'employees/dashboard.html', {
        'employees': employees,      # For the table
        'all_employees': employees   # For the navbar dropdown
    })

@login_required
def employee_list(request):
    # This is the new page showing all employees
    employees = Employee.objects.all()
    return render(request, 'employees/employee_list.html', {'employees': employees})


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

        data = {

            'name': request.POST['name'],

            'designation': request.POST['designation'],

            'emp_id': request.POST['emp_id'],

            'email': request.POST['email'],

            'phone': request.POST['phone'],

            'address': request.POST['address'],

            'basic_salary': request.POST['basic_salary'],

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
    'all_employees': Employee.objects.all() # Add this here
})

def payslip(request, pk):

    emp = get_object_or_404(Employee, pk=pk)

    context = {'emp': emp, 'payroll': emp.get_payroll_details()}

    return render(request, 'employees/payslip.html', context)

@login_required
def process_monthly_salary(request, emp_id):
    employee = get_object_or_404(Employee, id=emp_id)
    
    if request.method == "POST":
        # Create the record using the new model fields
        salary_record = MonthlySalary.objects.create(
            employee=employee,
            month=request.POST.get('month'),
            year=request.POST.get('year'),
            leaves_taken=int(request.POST.get('leaves', 0)),
            manual_mode=request.POST.get('manual_mode') == 'on',
            # Now these will NOT cause a TypeError
            da=float(request.POST.get('da', 0) or 0),
            hra=float(request.POST.get('hra', 0) or 0),
            pf=float(request.POST.get('pf', 0) or 0),
            esi=float(request.POST.get('esi', 0) or 0),
            custom_earnings=float(request.POST.get('custom_earnings', 0) or 0),
            custom_deductions=float(request.POST.get('custom_deductions', 0) or 0)
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