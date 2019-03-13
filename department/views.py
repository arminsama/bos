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
        kwargs['current_flag'] = 'department'
        kwargs['total_departments'] = Department.objects.all().count()
        return kwargs


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
