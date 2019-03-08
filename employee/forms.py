from django import forms
from .models import Employee


class EmployeeCreateForm(forms.ModelForm):
    password = forms.CharField(max_length=128, required=True, widget=forms.PasswordInput(), label='密码')

    class Meta:
        model = Employee
        fields = ['username', 'password', 'fullname', 'role', 'email', 'phone', 'productline', 'is_sa']


class EmployeeUpdateForm(forms.ModelForm):
    password = forms.CharField(max_length=128, required=False, widget=forms.PasswordInput(), label='密码')

    class Meta:
        model = Employee
        fields = ['username', 'password', 'fullname', 'role', 'email', 'phone', 'productline', 'is_sa']


class UserLoginForm(forms.Form):
    username = forms.CharField(max_length=128, label='用户名')
    password = forms.CharField(max_length=128, label='密码', widget=forms.PasswordInput())
