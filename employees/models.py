from django.db import models

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
    def get_payroll_details(self):
    
        da = (self.basic_salary * self.da_percent) / 100
        hra = (self.basic_salary * self.hra_percent) / 100
        other = (self.basic_salary * self.other_percent) / 100
        gross = self.basic_salary + da + hra + other
        pf = (gross * self.pf_percent) / 100
        esi = (gross * self.esi_percent) / 100
    
        return {
            'da': round(da, 2),
            'hra': round(hra, 2),
            'other': round(other, 2),
            'gross': round(gross, 2),
            'pf': round(pf, 2),
            'esi': round(esi, 2),
            'net': round(gross - (pf + esi), 2)
        }