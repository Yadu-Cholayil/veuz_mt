from django.urls import path

from employee.views import EmployeeListView, EmployeeDetailView, CustomFieldListView, CustomFieldDetailView, \
                            ChangePasswordView
from employee.template_views import login_page, employee_page, registration

urlpatterns = [
    path('employee/', EmployeeListView.as_view(), name='employee_list'),
    path('employee/<employee_uuid>/', EmployeeDetailView.as_view(), name='employee_detail'),
    path('employee/<employee_uuid>/field/', CustomFieldListView.as_view(), name='field_list'),
    path('employee/<employee_uuid>/field/<id>/', CustomFieldDetailView.as_view(), name='field_detail'),
    path('employee/<employee_uuid>/password/', ChangePasswordView.as_view(), name='change_password')

] # + [path('', login_page, name='page'),
  #   path('register/', registration, name='registration'),
  #   path('home/', employee_page, name='employee'),]