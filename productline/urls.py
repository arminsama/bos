from django.urls import path
from .views import ProductlineCreateView, ProductlineDeleteView, ProductlineListView, ProductlineUpdateView

urlpatterns = [
    path('', ProductlineListView.as_view(), name='productlines_list'),
    path('create/', ProductlineCreateView.as_view(), name='productline_create'),
    path('update/<int:pk>', ProductlineUpdateView.as_view(), name='productline_update'),
    path('delete/<int:pk>', ProductlineDeleteView.as_view(), name='productline_delete'),
]