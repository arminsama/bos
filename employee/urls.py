from django.urls import path
from .views import EmployeeListView, EmployeeCreateView, EmployeeDeleteView, EmployeeUpdateView, user_login, user_logout

urlpatterns = [
    path('', EmployeeListView.as_view(), name='employees_list'),
    path('create/', EmployeeCreateView.as_view(), name='employee_create'),
    path('update/<int:pk>', EmployeeUpdateView.as_view(), name='employee_update'),
    path('delete/<int:pk>', EmployeeDeleteView.as_view(), name='employee_delete'),
    path('login/', user_login, name='login'),
    path('logout/', user_logout, name='logout'),
]