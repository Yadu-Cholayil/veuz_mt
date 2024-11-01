from django.db import models
from django.contrib.auth.models import User

import uuid

# Create your models here.
class EmployeeProfile(models.Model):
    """Store employee details"""

    employee = models.OneToOneField(User, on_delete=models.CASCADE)
    employee_uuid = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False)
    phone_number = models.CharField(max_length=15)
    position = models.CharField(max_length=50)
    created_date = models.DateTimeField(auto_now_add=True)

    class meta:
        verbose_plural_name = 'Employee_Profiles'


class CustomField(models.Model):
    """Add extra fields to models"""

    employee = models.ForeignKey(EmployeeProfile, on_delete=models.DO_NOTHING, related_name="fields")
    field_name = models.CharField(max_length=50)
    field_content = models.CharField(max_length=128)