from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from utils.rootrequiredmixin import RootRequiredMixin
from django.views.generic import CreateView, ListView, UpdateView, DeleteView
from .models import ProductLine
from .forms import ProductlineCreateUpdateForm
# Create your views here.


class ProductlineListView(RootRequiredMixin, ListView):
    model = ProductLine
    context_object_name = 'productlines'
    template_name = 'productline/prodectlines_list.html'
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
        kwargs['current_flag'] = 'productline'
        kwargs['total_productlines'] = ProductLine.objects.all().count()
        return kwargs


class ProductlineCreateView(RootRequiredMixin, CreateView):
    model = ProductLine
    form_class = ProductlineCreateUpdateForm
    success_url = reverse_lazy('productlines:productlines_list')
    template_name = 'productline/prodectline_create.html'


class ProductlineUpdateView(RootRequiredMixin, UpdateView):
    model = ProductLine
    form_class = ProductlineCreateUpdateForm
    success_url = reverse_lazy('productlines:productlines_list')
    template_name = 'productline/prodectline_update.html'


class ProductlineDeleteView(RootRequiredMixin, DeleteView):
    model = ProductLine
    success_url = reverse_lazy('productlines:productlines_list')
    template_name = 'productline/prodectline_delete.html'
