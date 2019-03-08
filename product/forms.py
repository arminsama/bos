from django import forms
from .models import Product
from employee.models import Employee


class ProductCreateUpdateForm(forms.ModelForm):
    # def __init__(self, employee_choice, *args, **kwargs):
    #     super().__init__(*args, **kwargs)
        # self.fields['employee'].queryset = employee_choice

    #   产品拥有人为多个时， 必须为相同的组
    # employee = forms.ModelMultipleChoiceField(queryset=Employee.objects.none(), label='产品拥有人')

    class Meta:
        model = Product
        fields = ['name', 'comment', 'employees', 'domain', 'git_address', 'product_dir', 'sync_type', 'test_ip_list',
                  'gray_ip_list', 'online_ip_list', 'sync_option', 'no_sync_file_and_path', 'command_before_sync',
                  'command_after_sync', 'need_sa_agree', 'send_email', 'send_msg']
