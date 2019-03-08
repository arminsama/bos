from django.urls import path
from department.views import DepartmentListView, DepartmentCreateView, DepartmentUpdateView, DepartmentDeleteView


urlpatterns = [
    path('', DepartmentListView.as_view(), name='departments_list'),
    path('create/', DepartmentCreateView.as_view(), name='department_create'),
    path('update/<int:pk>', DepartmentUpdateView.as_view(), name='department_update'),
    path('delete/<int:pk>', DepartmentDeleteView.as_view(), name='department_delete'),
]
