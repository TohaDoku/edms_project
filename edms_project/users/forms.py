from django import forms
from .models import *

class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['title', 'description', 'executor', 'department', 'deadline']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Введите название поручения'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Описание поручения',
                'rows': 4
            }),
            'executor': forms.Select(attrs={
                'class': 'form-select'
            }),
            'department': forms.Select(attrs={
                'class': 'form-select'
            }),
            'deadline': forms.DateTimeInput(attrs={
                'type': 'datetime-local',
                'class': 'form-control'
            }),
        }


class DocumentReviewForm(forms.ModelForm):
    class Meta:
        model = Document
        fields = ['status', 'reviewer_comment']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-select'}),
            'reviewer_comment': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class DocumentCreateForm(forms.ModelForm):
    class Meta:
        model = Document
        fields = ['title', 'description', 'file', 'department']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'file': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'department': forms.Select(attrs={'class': 'form-select'}),
        }