from django.contrib import admin
from django.urls import path
from employees import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Auth
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # Employee Management
    path('', views.home, name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('add/', views.employee_form, name='employee_add'),
    path('edit/<int:pk>/', views.employee_form, name='employee_edit'),
    path('employees/', views.employee_list, name='employee_list'),
    
    # --- NEW: Monthly Salary Processing Paths ---
    
    # The page with the Dropdown & Month/Year/Leave inputs
    path('process-salary/<int:emp_id>/', views.process_monthly_salary, name='process_salary'),
    
    # The final monthly payslip (linked to MonthlySalary model PK)
    path('monthly-payslip/<int:pk>/', views.monthly_payslip, name='monthly_payslip'),
    
    # Original basic payslip (optional, keep if you still need the old version)
    path('payslip/<int:pk>/', views.payslip, name='payslip'),
    path('employee/<int:pk>/', views.employee_detail, name='employee_detail'),
    path('salary/edit/<int:pk>/', views.edit_monthly_salary, name='edit_monthly_salary'),
    # The "Specific" way (from employee profile)
    path('employee/<int:emp_id>/process/', views.process_monthly_salary, name='process_monthly_salary'),

# The "Global" way (Inexoft's new requirement)
    path('payroll/process/', views.global_monthly_process, name='global_monthly_process'),
    path('employees/list/', views.emp_full_list, name='employee_full_list'),
]