from django.db import models

class Employee(models.Model):
    # Fixed Details
    name = models.CharField(max_length=100)
    designation = models.CharField(max_length=100)
    emp_id = models.CharField(max_length=20, unique=True)
    email = models.EmailField()
    phone = models.CharField(max_length=15)
    address = models.TextField()
    
    # Base Salary Structure (for automatic calculation)
    basic_salary = models.FloatField()
    da_percent = models.FloatField(default=50)
    hra_percent = models.FloatField(default=40)
    other_percent = models.FloatField(default=10)
    pf_percent = models.FloatField(default=12)
    esi_percent = models.FloatField(default=0.75)

    def __str__(self):
        return f"{self.name} ({self.emp_id})"

class MonthlySalary(models.Model):
    # 1. The Dropdown Link
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='salaries')
    
    # 2. Month and Year Selection
    MONTH_CHOICES = [
        ('January', 'January'), ('February', 'February'), ('March', 'March'),
        ('April', 'April'), ('May', 'May'), ('June', 'June'),
        ('July', 'July'), ('August', 'August'), ('September', 'September'),
        ('October', 'October'), ('November', 'November'), ('December', 'December'),
    ]
    month = models.CharField(max_length=20, choices=MONTH_CHOICES)
    year = models.IntegerField(default=2026)
    
    # 3. Leave Management
    leaves_taken = models.IntegerField(default=0)
    
    # 4. Manual Override Fields
    # If these are filled, we use these values instead of auto-calculation
    manual_mode = models.BooleanField(default=False, help_text="Check this to enter values manually")
    custom_earnings = models.FloatField(default=0.0, blank=True, null=True)
    custom_deductions = models.FloatField(default=0.0, blank=True, null=True)

    # Storage for final results to show in Payslip
    calculated_gross = models.FloatField(null=True, blank=True)
    calculated_deduction = models.FloatField(null=True, blank=True)
    net_salary = models.FloatField(null=True, blank=True)

    def save(self, *args, **kwargs):
        """
        The Logic Engine: 
        Calculates salary based on Basic/Leaves OR Manual input before saving.
        """
        if self.manual_mode:
            # Manually entered values
            self.calculated_gross = self.custom_earnings
            self.calculated_deduction = self.custom_deductions
        else:
            # 1. Automatic Earnings Calculation
            basic = self.employee.basic_salary
            da = (basic * self.employee.da_percent) / 100
            hra = (basic * self.employee.hra_percent) / 100
            other = (basic * self.employee.other_percent) / 100
            gross = basic + da + hra + other
            
            # 2. Leave Deduction (Basic / 30 days * leaves)
            leave_cut = (basic / 30) * self.leaves_taken
            
            # 3. Statutory Deductions (PF/ESI)
            pf = (basic * self.employee.pf_percent) / 100
            esi = (basic * self.employee.esi_percent) / 100
            
            self.calculated_gross = gross
            self.calculated_deduction = pf + esi + leave_cut
        
        # Final Result
        self.net_salary = self.calculated_gross - self.calculated_deduction
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.employee.name} - {self.month} {self.year}"