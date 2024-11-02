from rest_framework import serializers

from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from employee.models import EmployeeProfile, CustomField

class EmployeeSerializer(serializers.ModelSerializer):

    full_name = serializers.SerializerMethodField()
    email = serializers.EmailField(source='employee.email', read_only=True)

    class Meta:
        model = EmployeeProfile
        fields = ['employee', 'employee_uuid', 'full_name', 'email', 'phone_number', 'position']

    def get_full_name(self, obj):
        full_name = "%s %s" % (obj.employee.first_name, obj.employee.last_name)
        return full_name.strip()
    

class CustomFieldSerializer(serializers.ModelSerializer):

    class Meta:
        model = CustomField
        fields = '__all__'


class MyTokenObtainSerializer(TokenObtainPairSerializer):

    def validate(self, attrs):
        data = super().validate(attrs)
        data['position'] = self.user.employeeprofile.position
        data['employee_uuid'] = self.user.employeeprofile.employee_uuid
        return data