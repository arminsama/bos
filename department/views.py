from django.views.generic import CreateView, ListView, UpdateView, DetailView, DeleteView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from utils.rootrequiredmixin import RootRequiredMixin
from department.models import Department
from department.forms import CreateUpdateDepartmentForm


class DepartmentListView(RootRequiredMixin, ListView):
    model = Department
    context_object_name = 'departments'
    template_name = 'department/departments_list.html'


class DepartmentCreateView(RootRequiredMixin, CreateView):
    model = Department
    template_name = 'department/department_create.html'
    form_class = CreateUpdateDepartmentForm
    success_url = reverse_lazy('departments:departments_list')


class DepartmentUpdateView(RootRequiredMixin, UpdateView):
    model = Department
    context_object_name = 'department'
    form_class = CreateUpdateDepartmentForm
    success_url = reverse_lazy('departments:departments_list')
    template_name = 'department/department_update.html'


class DepartmentDeleteView(RootRequiredMixin, DeleteView):
    model = Department
    context_object_name = 'department'
    success_url = reverse_lazy('departments:departments_list')
    template_name = 'department/department_delete.html'
