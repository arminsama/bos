from django import forms
from .models import Department


class CreateUpdateDepartmentForm(forms.ModelForm):
    forms.CharField()
    class Meta:
        model = Department
        fields = ['name', 'comment']

        widgets = {
            'name': forms.TimeInput(attrs={
                'class': 'form-control',
            }),

            'comment': forms.Textarea(attrs={
                'class': 'form-control',
            }),
        }

        labels = {
            'name': '部门',
            'comment': '部门信息',
        }

        error_messages = {
            'name': {'unique': '部门已存在请重新输入'},
        }
