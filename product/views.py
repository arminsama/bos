from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, DeleteView, CreateView, UpdateView
from utils.rootrequiredmixin import RootRequiredMixin
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Product
from .forms import ProductCreateUpdateForm
from employee.models import Employee
from utils.ip_valid_check import ip_list_check
from utils.rsyncd_conf_edit import rsync_config_add, rsync_config_del
# Create your views here.
"""项目名需要加验证"""


class ProductListView(RootRequiredMixin, ListView):
    model = Product
    context_object_name = 'products'
    template_name = 'product/products_list.html'
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
        kwargs['current_flag'] = 'product'
        kwargs['total_products'] = Product.objects.all().count()
        return kwargs


class ProductCreateView(RootRequiredMixin, CreateView):
    model = Product
    template_name = 'product/product_create.html'
    form_class = ProductCreateUpdateForm
    success_url = reverse_lazy('products:products_list')
    return_value = False
    error = ''
    product_name = ''

    def form_valid(self, form):
        self.return_value, ff = ip_list_check(self.request)
        if not self.return_value:
            self.error = '%s不规范，请重新填写' % ff
            return self.form_invalid(form)
        self.product_name = self.request.POST.get('name').strip()
        rsync_config_add(self.product_name)
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.error:
            context['error'] = self.error
        return context


class ProductUpdateView(RootRequiredMixin, UpdateView):
    model = Product
    template_name = 'product/product_update.html'
    context_object_name = 'product'
    form_class = ProductCreateUpdateForm
    success_url = reverse_lazy('products:products_list')
    return_value = False
    ip_check_error = ''
    rsyncd_config_change_error = ''
    product_name = ''
    old_product_name = ''

    def get_initial(self):
        old_product_id = self.kwargs['pk']
        self.old_product_name = Product.objects.get(pk=old_product_id).name
        return super().get_initial()

    def form_valid(self, form):
        self.return_value, ff = ip_list_check(self.request)
        if not self.return_value:
            self.ip_check_error = '%s不规范，请重新填写' % ff
            return self.form_invalid(form)
        self.product_name = self.request.POST.get('name').strip()
        ret = rsync_config_del(self.old_product_name)
        if ret:
            rsync_config_add(self.product_name)
        else:
            self.rsyncd_config_change_error = '配置文件修改失败,请手动编辑.'
            return super().form_valid(form)
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.ip_check_error:
            context['ip_check_error'] = self.ip_check_error
        if self.rsyncd_config_change_error:
            context['rsyncd_config_change_error'] = self.rsyncd_config_change_error
        return context


class ProductDetailView(LoginRequiredMixin, DetailView):
    model = Product
    context_object_name = 'product'
    template_name = 'product/product_detail.html'


class ProductDeleteView(RootRequiredMixin, DeleteView):
    model = Product
    context_object_name = 'product'
    template_name = 'product/product_delete.html'
    success_url = reverse_lazy('products:products_list')

    def post(self, request, *args, **kwargs):
        product = self.get_object()
        rsync_config_del(product.name)
        return super().post(request, *args, **kwargs)

