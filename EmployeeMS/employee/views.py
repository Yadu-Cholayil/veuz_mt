from django.contrib.auth import authenticate
from django.contrib.auth.hashers import make_password
from django.db import transaction

from rest_framework import status, filters
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView, UpdateAPIView, \
                                    ListAPIView, CreateAPIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from rest_framework_simplejwt.views import TokenObtainPairView

from employee.models import EmployeeProfile, User, CustomField
from employee.serializers import EmployeeSerializer, CustomFieldSerializer, UserSerializer, \
                                ProfileSerializer, MyTokenObtainSerializer 

# Create your views here.
class EmployeeListView(ListAPIView):
    """
        Employee registeration and listing API
    """
    serializer_class = EmployeeSerializer

    def get_queryset(self):
        owner = self.request.headers.get('position')
        print(owner)
        # TODO: add to permission class to authorize based on check with admin account. This method is insecure.
        if owner == "admin":
            return EmployeeProfile.objects.all()
        return EmployeeProfile.objects.filter(employee=self.request.user)


class EmployeeRegisterView(CreateAPIView):

    serializer_class = EmployeeSerializer
    permission_classes = [AllowAny,]
    queryset = EmployeeProfile.objects.all()
    
    @transaction.atomic
    def post(self, request, *args, **kwargs):
        data = request.data

        # TODO: move this check into serializer validators.
        if data.get('password2'):
            if str(data['password']) != str(data['password2']):
                return Response({'error': 'Password and Password2 does not match'})

        user_data = {'username' : data.pop('username'),
         'first_name': data.pop('first_name'),
         'last_name' : data.pop('last_name'),
         'password': make_password(str(data.pop('password'))),
         'email' : data.pop('email')
         }

        try:
            user = User.objects.create(**user_data)
            data['employee'] = user.id

            serializer = self.get_serializer(data=data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        except Exception as E:
            print(E.args)
            return Response(E.args, status=status.HTTP_400_BAD_REQUEST)
        

class EmployeeDetailView(RetrieveUpdateDestroyAPIView):

    serializer_class = ProfileSerializer
    queryset = EmployeeProfile.objects.all()

    def get_object(self):
        return EmployeeProfile.objects.filter(employee_uuid=self.kwargs['employee_uuid']).first()
    
    # def get(self, request, *args, **kwargs):
    #     instance = self.get_object()
    #     fields = instance.fields.all()
        
    #     combined_data = {
    #         'employee': self.get_serializer(instance).data,
    #         'fields' : CustomFieldSerializer(fields, many=True).data if fields else None,
    #     }
    #     return Response(combined_data, status=status.HTTP_200_OK)
        

    def patch(self, request, *args, **kwargs):
        data = request.data
        employee = self.get_object()
        user = employee.employee
        custom_fields = employee.fields.all()

        user_data = data['user_info']
        contact_data = data['contact_info']
        field_data = data['custom_fields']
        
        user = UserSerializer(user, data=user_data, partial=True)
        user.is_valid(raise_exception=True)
        user.save()

        custom_fields.delete()
        print(field_data)
        for field in field_data:
            field['employee'] = self.kwargs['employee_uuid']
            fieldserializer = CustomFieldSerializer(data=field)
            fieldserializer.is_valid(raise_exception=True)
            fieldserializer.save()

        serializer = self.get_serializer(employee, data=contact_data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)
    
    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        user = instance.employee
        print(user)
        user.delete()
        return Response("Successfully deleted")
    

class ChangePasswordView(UpdateAPIView):

    serializer_class = EmployeeSerializer
    queryset = EmployeeProfile.objects.all()

    def get_object(self):
        return EmployeeProfile.objects.filter(employee_uuid=self.kwargs['employee_uuid']).first()
    
    def put(self, request, *args, **kwargs):
        return Response('Please use Patch method to reset password', status=status.HTTP_403_FORBIDDEN) 

    def patch(self, request, *args, **kwargs):
        data = request.data

        instance = self.get_object().employee
        user = authenticate(request=self.request, username=instance.username, password=data['old_password'])

        if user is None:
            return Response('Invalid credentials', status=status.HTTP_401_UNAUTHORIZED)
        
        if str(data['new_password']) != str(data['new_password_2']):
                return Response({'error': 'Password and Password_2 does not match'})
        
        instance.password = make_password(str(data['new_password']))
        instance.save()
        return Response("Successfully saved", status=status.HTTP_200_OK)


class CustomFieldListView(ListCreateAPIView):

    serializer_class = CustomFieldSerializer
    
    def get_queryset(self):
        return CustomField.objects.filter(employee = self.kwargs['employee_uuid'])

    def post(self, request, *args, **kwargs):
        data = request.data.copy()

        data['employee'] = self.kwargs['employee_uuid']

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        return Response(serializer.data, status=status.HTTP_201_CREATED)


class CustomFieldDetailView(RetrieveUpdateDestroyAPIView):

    serializer_class = CustomFieldSerializer
    queryset = CustomField.objects.all()

    def get_object(self):
        return CustomField.objects.filter(employee_uuid = self.kwargs['employee_uuid']).first()


class MyObtainTokenPairView(TokenObtainPairView):

    serializer_class = MyTokenObtainSerializer
    permission_classes = [AllowAny,]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        token = serializer.validated_data['access']
        refresh = serializer.validated_data['refresh']

        # Prepare the custom response
        response_data = {
            'refresh': refresh,
            'access': token,
            'position': serializer.validated_data['position'],  # Custom claim
            'employee_uuid': serializer.validated_data['employee_uuid'],
        }
        
        return Response(response_data, status=status.HTTP_200_OK)