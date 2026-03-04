from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import logout as django_logout
from django.contrib.auth.decorators import login_required
from .models import Employee, MonthlySalary # Import your new model here

# ... (home, dashboard, logout_view, employee_form remain the same) ...
def home(request):

    return redirect('employees/dashboard.html')



@login_required
def dashboard(request):
    # We call it 'all_employees' so the navbar dropdown can see it
    employees = Employee.objects.all()
    return render(request, 'employees/dashboard.html', {
        'employees': employees,      # For the table
        'all_employees': employees   # For the navbar dropdown
    })


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
def process_monthly_salary(request):
    """
    New view to handle selecting an employee and calculating 
    their monthly salary with manual override options.
    """
    employees = Employee.objects.all()
    
    if request.method == "POST":
        # 1. Get Employee from Dropdown
        emp_id = request.POST.get('employee_id')
        employee = get_object_or_404(Employee, id=emp_id)
        
        # 2. Get Month, Year, and Leaves
        month = request.POST.get('month')
        year = request.POST.get('year')
        leaves = int(request.POST.get('leaves', 0))
        
        # 3. Handle Manual Mode logic
        is_manual = request.POST.get('manual_mode') == 'on'
        manual_earn = float(request.POST.get('custom_earnings', 0) or 0)
        manual_deduct = float(request.POST.get('custom_deductions', 0) or 0)

        # 4. Create and Save the MonthlySalary record
        # The .save() method in the model will handle the math automatically
        salary_record = MonthlySalary.objects.create(
            employee=employee,
            month=month,
            year=year,
            leaves_taken=leaves,
            manual_mode=is_manual,
            custom_earnings=manual_earn,
            custom_deductions=manual_deduct
        )
        
        # 5. Redirect to the payslip of this specific monthly record
        return redirect('monthly_payslip', pk=salary_record.pk)

    return render(request, 'employees/salary_process_form.html', {'employees': employees})

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