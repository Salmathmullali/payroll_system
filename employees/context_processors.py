# employees/context_processors.py
from .models import Employee

def employee_list(request):
    return {
        'all_employees': Employee.objects.all()
    }