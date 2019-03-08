from django.shortcuts import render, redirect, HttpResponse
from django.views.generic import CreateView, ListView, UpdateView, DetailView, DeleteView
from django.urls import reverse_lazy
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from utils.rootrequiredmixin import RootRequiredMixin
from .models import Employee
from .forms import EmployeeCreateForm, EmployeeUpdateForm, UserLoginForm


class EmployeeListView(LoginRequiredMixin, ListView):
    model = Employee
    context_object_name = 'employees'
    template_name = 'employee/employees_list.html'

    # def get_queryset(self):
    #     if self.request.user.is_root:
    #         return super().get_queryset()
    #     else:
    #         return Employee.objects.filter(username=self.request.user.username)


class EmployeeCreateView(RootRequiredMixin, CreateView):
    model = Employee
    form_class = EmployeeCreateForm
    success_url = reverse_lazy('employees:employees_list')
    template_name = 'employee/employee_create.html'
    
    def form_valid(self, form):
        employee = form.save(commit=False)
        password = self.request.POST.get('password', 'feeyo#1234')
        employee.set_password(password)
        return super().form_valid(form)

    def form_invalid(self, form):
        return super().form_invalid(form)


class EmployeeUpdateView(RootRequiredMixin, UpdateView):
    model = Employee
    context_object_name = 'employee'
    form_class = EmployeeUpdateForm
    success_url = reverse_lazy('employees:employees_list')
    template_name = 'employee/employee_update.html'

    def form_valid(self, form):
        employee = form.save(commit=False)
        password = self.request.POST.get('password', '')
        if password:
            employee.set_password(password)
        else:
            employee.password = Employee.objects.get(username=employee.username).password
        return super().form_valid(form)


class EmployeeDeleteView(RootRequiredMixin, DeleteView):
    model = Employee
    context_object_name = 'employee'
    success_url = reverse_lazy('employees:employees_list')
    template_name = 'employee/employee_delete.html'


def user_login(request):
    error = ''
    user_login_form = UserLoginForm
    next_url = request.GET.get('next', '/')
    if request.method == 'POST':
        username = request.POST.get('username', None)
        password = request.POST.get('password', None)
        user = authenticate(username=username, password=password)
        next_url = request.POST.get('next', '/')
        if user:
            if user.is_active:
                login(request, user)
                return redirect(next_url)
            else:
                return HttpResponse('该用户被禁止登录')
        else:
            error = 'bad username or password'

    return render(request, 'employee/employee_login.html', context={'user_login_form': user_login_form,
                                                                    'error': error, 'next_url': next_url})


def user_logout(request):
    logout(request)
    return redirect(reverse_lazy('employees:login'))
