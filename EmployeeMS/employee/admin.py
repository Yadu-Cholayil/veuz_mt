from django.contrib import admin

from employee.models import EmployeeProfile, CustomField
# Register your models here.

admin.site.register(EmployeeProfile)
admin.site.register(CustomField)