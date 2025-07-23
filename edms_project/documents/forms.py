from django import forms
from .models import *
from django.contrib.auth import get_user_model

class IncomingDocumentForm(forms.ModelForm):
    class Meta:
        model = IncomingDocument
        fields = ['title', 'content', 'sender', 'received_date', 'category', 'file']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'sender': forms.TextInput(attrs={'class': 'form-control'}),
            'received_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'file': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }


User = get_user_model()

class DocumentRouteForm(forms.ModelForm):
    assigned_to = forms.ModelChoiceField(
        queryset=User.objects.all(),
        label="Назначить сотрудника",
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    due_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        required=False,
        label="Срок исполнения"
    )

    comment = forms.CharField(
        label="Комментарий / резолюция",
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3})
    )

    class Meta:
        model = DocumentRoute
        fields = ['assigned_to', 'due_date', 'comment']


class OutgoingDocumentForm(forms.ModelForm):
    class Meta:
        model = OutgoingDocument
        fields = ['title', 'content', 'recipient', 'file']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
            'recipient': forms.TextInput(attrs={'class': 'form-control'}),
            'file': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }