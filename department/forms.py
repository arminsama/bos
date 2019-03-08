from django import forms
from .models import Department


class CreateUpdateDepartmentForm(forms.ModelForm):
    class Meta:
        model = Department
        fields = ['name', 'comment']
