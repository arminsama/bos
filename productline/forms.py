from django import forms
from .models import ProductLine


class ProductlineCreateUpdateForm(forms.ModelForm):
    class Meta:
        model = ProductLine
        fields = ['name', 'department', 'administrator']
