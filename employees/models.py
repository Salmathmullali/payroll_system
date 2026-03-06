from django.db import models


MONTH_CHOICES = [
    ('January', 'January'), ('February', 'February'), ('March', 'March'),
    ('April', 'April'), ('May', 'May'), ('June', 'June'),
    ('July', 'July'), ('August', 'August'), ('September', 'September'),
    ('October', 'October'), ('November', 'November'), ('December', 'December'),
]

class Employee(models.Model):
    
    name = models.CharField(max_length=100)
    designation = models.CharField(max_length=100)
    emp_id = models.CharField(max_length=20, unique=True)
    email = models.EmailField()
    phone = models.CharField(max_length=15)
    address = models.TextField()
    
    
    basic_salary = models.FloatField()
    da_percent = models.FloatField(default=50)
    hra_percent = models.FloatField(default=40)
    other_percent = models.FloatField(default=10)
    pf_percent = models.FloatField(default=12)
    esi_percent = models.FloatField(default=0.75)

    def __str__(self):
        return f"{self.name} ({self.emp_id})"

class MonthlySalary(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='salaries')
    month = models.CharField(max_length=20, choices=MONTH_CHOICES)
    year = models.IntegerField(default=2026)
    leaves_taken = models.IntegerField(default=0)
    
    
    da = models.FloatField(default=0.0, blank=True, null=True)
    hra = models.FloatField(default=0.0, blank=True, null=True)
    pf = models.FloatField(default=0.0, blank=True, null=True)
    esi = models.FloatField(default=0.0, blank=True, null=True)

   
    manual_mode = models.BooleanField(default=False, help_text="Check to enter total values manually")
    custom_earnings = models.FloatField(default=0.0, blank=True, null=True)
    custom_deductions = models.FloatField(default=0.0, blank=True, null=True)

    
    calculated_gross = models.FloatField(null=True, blank=True)
    calculated_deduction = models.FloatField(null=True, blank=True)
    net_salary = models.FloatField(null=True, blank=True)

    def save(self, *args, **kwargs):
        
        if self.manual_mode:
            
            self.calculated_gross = self.custom_earnings
            self.calculated_deduction = self.custom_deductions
        else:
            basic = self.employee.basic_salary
            
            da_val = self.da if (self.da and self.da > 0) else (basic * self.employee.da_percent / 100)
            hra_val = self.hra if (self.hra and self.hra > 0) else (basic * self.employee.hra_percent / 100)
            other = (basic * self.employee.other_percent) / 100
            
            pf_val = self.pf if (self.pf and self.pf > 0) else (basic * self.employee.pf_percent / 100)
            esi_val = self.esi if (self.esi and self.esi > 0) else (basic * self.employee.esi_percent / 100)
            
            
            leave_cut = (basic / 30) * self.leaves_taken

            self.calculated_gross = basic + da_val + hra_val + other
            self.calculated_deduction = pf_val + esi_val + leave_cut
        
       
        self.net_salary = self.calculated_gross - self.calculated_deduction
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.employee.name} - {self.month} {self.year}"