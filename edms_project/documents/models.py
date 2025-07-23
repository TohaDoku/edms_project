from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.conf import settings

User = get_user_model()


class IncomingDocument(models.Model):
    CATEGORY_CHOICES = [
        ('Договор', 'Договор'),
        ('Жалоба', 'Жалоба'),
        ('Финансы', 'Финансовый документ'),
        ('Распоряжение', 'Распорядительный документ'),
        ('Заявление', 'Заявление'),
        ('Прочее', 'Прочее'),
    ]

    number = models.CharField("Регистрационный номер", max_length=50, unique=True)
    title = models.CharField("Тема документа", max_length=255)
    content = models.TextField("Содержание", blank=True)
    category = models.CharField("Категория", max_length=100, choices=CATEGORY_CHOICES, blank=True)
    sender = models.CharField("Отправитель", max_length=255)
    received_date = models.DateField("Дата получения", default=timezone.now)
    file = models.FileField("Файл документа", upload_to="incoming/")
    registered_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name="Зарегистрировал")
    created_at = models.DateTimeField("Дата регистрации", auto_now_add=True)


class WorkflowStatus(models.TextChoices):
    REVIEW = 'review', 'На рассмотрении'
    APPROVED = 'approved', 'Согласован'
    COMPLETED = 'completed', 'Исполнен'


class DocumentRoute(models.Model):
    document = models.ForeignKey(IncomingDocument, on_delete=models.CASCADE, related_name='routes')
    assigned_to = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='assigned_documents')
    status = models.CharField(max_length=20, choices=WorkflowStatus.choices, default=WorkflowStatus.REVIEW)
    comment = models.TextField("Комментарий/резолюция", blank=True)
    due_date = models.DateField("Срок исполнения", null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.document.number} → {self.assigned_to} ({self.get_status_display()})"
    

class OutgoingDocument(models.Model):
    number = models.CharField("Регистрационный номер", max_length=50, unique=True)
    title = models.CharField("Заголовок", max_length=255)
    content = models.TextField("Текст документа")
    recipient = models.CharField("Получатель", max_length=255)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='outgoing_created')
    file = models.FileField("Приложение", upload_to='outgoing/', blank=True, null=True)
    status = models.CharField(max_length=20, choices=[
        ('draft', 'Черновик'),
        ('on_approval', 'На согласовании'),
        ('sent', 'Отправлен'),
    ], default='draft')
    created_at = models.DateTimeField(auto_now_add=True)
    sent_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.number} — {self.title}"