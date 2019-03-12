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
    paginate_by = 8
    page_kwarg = 'page'
    ordering = ['id']

    def __init__(self):
        super().__init__()
        #   当前页面
        self.current_page = 0
        #   用于前端展示页码范围
        self.page_range = ''

    def get_paginator(self, queryset, per_page, orphans=0,
                      allow_empty_first_page=True, **kwargs):
        #   计算当前页,获取分页信息
        self.current_page = int(self.request.GET.get(self.page_kwarg, 1))
        paginator = super().get_paginator(queryset, per_page, **kwargs)
        if paginator.num_pages > 7:
            if (self.current_page - 3) < 1:
                self.page_range = range(1, 8)
            elif (self.current_page + 3) > paginator.num_pages:
                self.page_range = range(paginator.num_pages - 6, paginator.num_pages + 1)
            else:
                self.page_range = range(self.current_page - 3, self.current_page + 4)
        else:
            self.page_range = paginator.page_range
        return paginator

    def get_context_data(self, *, object_list=None, **kwargs):
        kwargs = super().get_context_data(**kwargs)
        #   获取get_paginator() 获取的页面范围
        kwargs['page_range'] = self.page_range
        kwargs['current_flag'] = 'employee'
        return kwargs


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
