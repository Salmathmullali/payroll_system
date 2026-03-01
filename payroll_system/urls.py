from django.contrib import admin
from django.urls import path
from employees import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('', views.dashboard, name='dashboard'), 
    path('add/', views.employee_form, name='employee_add'),
    path('edit/<int:pk>/', views.employee_form, name='employee_edit'),
    path('payslip/<int:pk>/', views.payslip, name='payslip'),
]