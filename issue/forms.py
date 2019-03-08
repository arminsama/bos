from django import forms
from .models import Issue
from product.models import Product
from employee.models import Employee


class IssueCreateForm(forms.ModelForm):
    def __init__(self, *args, product_name_list, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['product_name'].queryset = product_name_list

    product_name = forms.ModelChoiceField(queryset=Product.objects.none(), label='产品名')

    class Meta:
        model = Issue
        fields = ['title', 'comment', 'product_name']
