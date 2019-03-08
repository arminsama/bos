from django.urls import path
from .views import ProductCreateView, ProductListView, ProductUpdateView, ProductDeleteView, ProductDetailView

urlpatterns = [
    path('', ProductListView.as_view(), name='products_list'),
    path('create/', ProductCreateView.as_view(), name='product_create'),
    path('detail/<int:pk>', ProductDetailView.as_view(), name='product_detail'),
    path('update/<int:pk>', ProductUpdateView.as_view(), name='product_update'),
    path('delete/<int:pk>', ProductDeleteView.as_view(), name='product_delete'),
]
