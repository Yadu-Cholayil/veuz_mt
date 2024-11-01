from django.contrib.auth import authenticate
from django.contrib.auth.hashers import make_password

from rest_framework import status, filters
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView, UpdateAPIView
from rest_framework.response import Response

from rest_framework_simplejwt.views import TokenObtainPairView

from employee.models import EmployeeProfile, User, CustomField
from employee.serializers import EmployeeSerializer, CustomFieldSerializer, MyTokenObtainSerializer

# Create your views here.
class EmployeeListView(ListCreateAPIView):
    """
        Employee registeration and listing API
    """
    serializer_class = EmployeeSerializer

    def get_queryset(self):
        owner = self.request.headers.get('position')
        # TODO: add uuid and position to header and add permission class to authorize based on check with admin account.
        if owner == "admin":
            return EmployeeProfile.objects.all()
        return EmployeeProfile.objects.filter(employee=self.request.user)


    def post(self, request, *args, **kwargs):
        data = request.data

        # TODO: move this check into serializer validators.
        if data['password2']:
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
            print(E)
            return Response(serializer.err, status=status.HTTP_400_BAD_REQUEST)


class EmployeeDetailView(RetrieveUpdateDestroyAPIView):

    serializer_class = EmployeeSerializer
    queryset = EmployeeProfile.objects.all()

    def get_object(self):
        return EmployeeProfile.objects.filter(employee_uuid=self.kwargs['employee_uuid']).first()

    def patch(self, request, *args, **kwargs):
        data = request.data
        employee = self.get_object()

        fields = ['username', 'first_name', 'last_name', 'email']
        user = employee.employee
        for item in fields:
            if item in data:
                setattr(user, item, data[item])

                user.save()

        serializer = self.get_serializer(employee, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)
    
    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        user = instance.employee
        user.delete()
        return Response("Successfully deleted")
    

class ChangePasswordView(UpdateAPIView):

    serializer_class = EmployeeSerializer
    queryset = EmployeeProfile.objects.all()

    def get_object(self):
        return EmployeeProfile.objects.filter(employee=self.kwargs['employee_uuid']).first()
    
    def put(self, request, *args, **kwargs):
        return Response('Please use Patch method to reset password', status=status.HTTP_403_FORBIDDEN) 

    def patch(self, request, *args, **kwargs):
        data = request.data

        instance = self.get_object().employee
        user = authenticate(request=self.context.get('request'), username=instance.username, password=data['old_password'])

        if user is None:
            return Response('Invalid credentials', status=status.HTTP_401_UNAUTHORIZED)
        
        if str(data['new_password']) != str(data['new_password_2']):
                return Response({'error': 'Password and Password_2 does not match'})
        
        instance.save(password=data['new_password'])
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
        return CustomField.objects.filter(employee = self.kwargs['employee_uuid'])


class MyObtainTokenPairView(TokenObtainPairView):

    serializer_class = MyTokenObtainSerializer

    def post(self, request, *args, **kwargs):
        # Validate the request and get the token
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Extract the token and custom claims
        token = serializer.validated_data['access']
        refresh = serializer.validated_data['refresh']

        # Prepare the custom response
        response_data = {
            'refresh': refresh,
            'access': token,
            'position': serializer.validated_data['position'],  # Custom claim
        }
        
        return Response(response_data)