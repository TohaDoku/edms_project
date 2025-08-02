from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class LoginLog(models.Model):
    EVENT_TYPE_CHOICES = [
        ('login_success', 'Успешный вход'),
        ('login_failed', 'Неудачная попытка входа'),
    ]

    username = models.CharField(max_length=150)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    event_type = models.CharField(max_length=20, choices=EVENT_TYPE_CHOICES)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.get_event_type_display()} - {self.username} ({self.timestamp})"


class Department(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

class Task(models.Model):
    title = models.CharField("Название поручения", max_length=255)
    description = models.TextField("Описание", blank=True)
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name="created_tasks")
    executor = models.ForeignKey(User, on_delete=models.CASCADE, related_name="assigned_tasks")
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    deadline = models.DateTimeField("Дедлайн")
    created_at = models.DateTimeField(auto_now_add=True)
    is_completed = models.BooleanField(default=False)

    def __str__(self):
        return self.title


class Document(models.Model):
    STATUS_CHOICES = [
        ('на согласовании', 'На согласовании'),
        ('одобрен', 'Одобрен'),
        ('на доработке', 'На доработке'),
    ]

    title = models.CharField(max_length=255)
    description = models.TextField("Краткое описание", blank=True)
    file = models.FileField(upload_to='documents/')
    department = models.ForeignKey('Department', on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='на согласовании')
    reviewer_comment = models.TextField("Комментарий руководителя", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title