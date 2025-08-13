from django.contrib.auth.views import LoginView
from django.views.generic import ListView
from django.contrib.auth.decorators import user_passes_test
from django.utils.decorators import method_decorator
from .models import *
from .forms import *
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from datetime import timedelta


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    return x_forwarded_for.split(',')[0] if x_forwarded_for else request.META.get('REMOTE_ADDR')


class CustomLoginView(LoginView):
    template_name = 'users/login.html'

    def form_valid(self, form):
        response = super().form_valid(form)
        from .models import LoginLog
        LoginLog.objects.create(
            username=self.request.user.username,
            user=self.request.user,
            ip_address=get_client_ip(self.request),
            user_agent=self.request.META.get('HTTP_USER_AGENT', ''),
            event_type='login_success'
        )
        return response

    def form_invalid(self, form):
        from .models import LoginLog
        username = self.request.POST.get('username', 'Неизвестно')
        LoginLog.objects.create(
            username=username,
            ip_address=get_client_ip(self.request),
            user_agent=self.request.META.get('HTTP_USER_AGENT', ''),
            event_type='login_failed'
        )
        return super().form_invalid(form)



class LoginLogListView(ListView):
    model = LoginLog
    template_name = 'users/login_journal.html'
    context_object_name = 'logs'
    ordering = ['-timestamp']
    paginate_by = 30


@login_required
def dashboard(request):
    user = request.user
    now = timezone.now().date()
    start_of_week = now - timedelta(days=now.weekday())
    end_of_week = start_of_week + timedelta(days=6)

    # Мои поручения (я исполнитель)
    my_tasks = Task.objects.filter(executor=user, is_completed=False)

    my_tasks_today = my_tasks.filter(deadline=now).count()
    my_tasks_1_3 = my_tasks.filter(deadline__gt=now, deadline__lte=now + timedelta(days=3)).count()
    my_tasks_week = my_tasks.filter(deadline__gt=now + timedelta(days=3), deadline__lte=end_of_week).count()
    my_tasks_late = my_tasks.filter(deadline__gt=end_of_week).count()
    my_tasks_overdue = my_tasks.filter(deadline__lt=now).count()
    my_tasks_total = my_tasks.count()

    # Назначенные поручения (я руководитель)
    assigned_tasks = Task.objects.filter(creator=user, is_completed=False)

    assigned_today = assigned_tasks.filter(deadline=now).count()
    assigned_1_3 = assigned_tasks.filter(deadline__gt=now, deadline__lte=now + timedelta(days=3)).count()
    assigned_week = assigned_tasks.filter(deadline__gt=now + timedelta(days=3), deadline__lte=end_of_week).count()
    assigned_late = assigned_tasks.filter(deadline__gt=end_of_week).count()
    assigned_overdue = assigned_tasks.filter(deadline__lt=now).count()
    assigned_total = assigned_tasks.count()

    # Документы
    documents_pending = Document.objects.filter(executor=user, status='на согласовании').count()
    documents_returned = Document.objects.filter(creator=user, status='на доработке').count()
    documents_incoming = Document.objects.filter(executor=user, status='на согласовании').count()

    context = {
        'user_display': f"{user.last_name} {user.first_name[0]}.",
        'my_tasks': {
            'today': my_tasks_today,
            '1_3': my_tasks_1_3,
            'week': my_tasks_week,
            'late': my_tasks_late,
            'overdue': my_tasks_overdue,
            'total': my_tasks_total,
        },
        'assigned_tasks': {
            'today': assigned_today,
            '1_3': assigned_1_3,
            'week': assigned_week,
            'late': assigned_late,
            'overdue': assigned_overdue,
            'total': assigned_total,
        },
        'documents_pending': documents_pending,
        'documents_returned': documents_returned,
        'documents_incoming': documents_incoming,
        'is_leader': user.groups.filter(name='Руководитель').exists()
    }

    return render(request, 'users/dashboard.html', context)

@login_required
def create_task(request):
    #if not request.user.groups.filter(name='department_heads').exists():
    #    return redirect('no_access')  # ограничение по правам

    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.creator = request.user
            task.save()
            return redirect('task_list')
    else:
        form = TaskForm()
    return render(request, 'users/create_task.html', {'form': form})

@login_required
def task_list(request):
    tasks = Task.objects.filter(executor=request.user, is_completed=False, deadline__gte=timezone.now()).order_by('deadline')
    return render(request, 'users/task_list.html', {'tasks': tasks})


@login_required
def documents_for_review(request):
    documents = Document.objects.filter(executor=request.user, status='на согласовании')
    return render(request, 'users/review_list.html', {'documents': documents})

@login_required
def review_document(request, doc_id):
    document = get_object_or_404(Document, pk=doc_id)
    leaders = User.objects.filter(groups__name__in=["Руководитель", "Администратор"]).order_by('last_name', 'first_name')
    # Получаем список групп пользователя
    user_groups = request.user.groups.values_list('name', flat=True)
    is_employee = 'Сотрудник' in user_groups

    if request.method == 'POST':
        if is_employee:
            form = DocumentFileUploadForm(request.POST, request.FILES, instance=document)
            if form.is_valid():
                doc = form.save(commit=False)
                doc.status = 'на согласовании'  # статус по умолчанию
                doc.save()

                # логируем действие
                DocumentActionLog.objects.create(
                    document=doc,
                    user=request.user,
                    action='повторно отправлен' if 'на доработке' in document.status else 'отправлен на согласование'
                )
                return redirect('documents_for_review')
        else:
            form = DocumentReviewForm(request.POST, instance=document)
            if form.is_valid():
                prev_status = document.status
                doc = form.save()

                # определяем действие
                if prev_status == 'на согласовании' and doc.status == 'на доработке':
                    action = 'отправлен на доработку'
                elif prev_status == 'на доработке' and doc.status == 'на согласовании':
                    action = 'повторно отправлен'
                else:
                    action = f'статус изменён на "{doc.get_status_display()}"'

                DocumentActionLog.objects.create(
                    document=doc,
                    user=request.user,
                    action=action
                )
                return redirect('documents_for_review')
    else:
        form = DocumentFileUploadForm(instance=document) if is_employee else DocumentReviewForm(instance=document)

    return render(request, 'users/review_form.html', {
        'form': form,
        'document': document,
        'is_employee': is_employee,
        'leaders': leaders
    })


@login_required
def archive_view(request):
    documents = Document.objects.exclude(status__in=['на согласовании', 'на доработке']).order_by('-created_at')
    return render(request, 'users/archive.html', {'documents': documents})


@login_required
def create_document(request):
    if request.method == 'POST':
        form = DocumentCreateForm(request.POST, request.FILES)
        if form.is_valid():
            document = form.save(commit=False)
            document.creator = request.user
            document.save()
            return redirect('documents_for_review')
    else:
        form = DocumentCreateForm()

    return render(request, 'users/create_document.html', {'form': form})


@login_required
def document_detail(request, document_id):
    doc = get_object_or_404(Document, id=document_id)
    return render(request, 'users/document_detail.html', {'doc': doc})


@login_required
def staff_structure_view(request):
    users_without_department = User.objects.filter(departments=None)
    departments = Department.objects.prefetch_related('users').all()

    return render(request, 'users/staff_structure.html', {
        'users_without_department': users_without_department,
        'departments': departments,
    })


@login_required
def documents_for_update(request):
    documents = Document.objects.filter(creator=request.user, status='на доработке')
    return render(request, 'users/review_list.html', {'documents': documents})


@login_required
def change_document_executor(request, document_id):
    document = get_object_or_404(Document, id=document_id)

    # Проверка прав — например, только создатель документа или админ
    if request.user != document.creator and not request.user.is_superuser:
        return redirect('document_detail', document_id=document.id)

    if request.method == "POST":
        new_executor_id = request.POST.get("executor")
        if new_executor_id:
            new_executor = get_object_or_404(User, id=new_executor_id)
            document.executor = new_executor
            document.save()

            # Логируем действие
            DocumentActionLog.objects.create(
                document=document,
                user=request.user,
                action=f'Согласующий изменён на {new_executor.get_full_name() or new_executor.username}'
            )

    return redirect('review_document', document_id=document.id)


@login_required
def complete_task(request, task_id):
    task = get_object_or_404(Task, id=task_id, executor=request.user)
    task.is_completed = True
    task.save()
    return redirect('task_list')


@login_required
def edit_task(request, task_id):
    task = get_object_or_404(Task, id=task_id)

    # Проверка прав — только исполнитель или создатель
    if task.executor != request.user and task.creator != request.user:
        return redirect('task_list')

    if request.method == 'POST':
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            form.save()
            return redirect('task_list')
    else:
        form = TaskForm(instance=task)

    return render(request, 'users/edit_task.html', {'form': form, 'task': task})