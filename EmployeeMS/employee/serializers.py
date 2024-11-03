from rest_framework import serializers

from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from employee.models import EmployeeProfile, CustomField, User


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']


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


class ProfileSerializer(serializers.ModelSerializer):

    user = UserSerializer(source='employee', read_only=True)
    fields = CustomFieldSerializer(many=True, read_only=True)

    class Meta:
        model = EmployeeProfile
        fields = ['phone_number', 'position', 'created_date', 'user', 'fields']