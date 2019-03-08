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
