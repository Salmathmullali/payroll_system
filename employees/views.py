from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import logout as django_logout
from django.contrib.auth.decorators import login_required
from .models import Employee

def home(request):
    return redirect('employees/base.html')
@login_required
def dashboard(request):
    employees = Employee.objects.all()
    return render(request, 'employees/dashboard.html', {'employees': employees})

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

    return render(request, 'employees/employee_form.html', {'employee': employee})
def payslip(request, pk):
    emp = get_object_or_404(Employee, pk=pk)
    context = {'emp': emp, 'payroll': emp.get_payroll_details()}
    return render(request, 'employees/payslip.html', context)