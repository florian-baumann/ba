from django import forms
from django.forms import ModelForm
from .models import Users


class UserForm(forms.ModelForm):
    class Meta:
        model = Users
        fields = "__all__"  # include all fields in form