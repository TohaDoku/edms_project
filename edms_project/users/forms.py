from django import forms
from .models import *
from django.contrib.auth.models import User, Group

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
        fields = ['title', 'type_choices', 'executor', 'file']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'type_choices': forms.Select(attrs={'class': 'form-select'}),
            'file': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'executor': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Фильтрация пользователей по группам
        self.fields['executor'].queryset = User.objects.filter(
            groups__name__in=['Администратор', 'Руководитель']
        ).distinct()

        # Отображение Фамилия Имя вместо username
        self.fields['executor'].label_from_instance = lambda obj: f"{obj.last_name} {obj.first_name}".strip() or obj.username


class DocumentFileUploadForm(forms.ModelForm):
    class Meta:
        model = Document
        fields = ['file']  # только поле для файла
        widgets = {
            'file': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }