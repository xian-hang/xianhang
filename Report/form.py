from django import forms
from .models import ReportImage

class ReportImageForm(forms.ModelForm):
    class Meta:
        model = ReportImage
        fields = ('image',)