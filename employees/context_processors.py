from .models import Employee

def employee_context(request):
    return {
        'all_employees': Employee.objects.all()
    }