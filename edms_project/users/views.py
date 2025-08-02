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


@method_decorator(user_passes_test(lambda u: u.is_superuser), name='dispatch')
class LoginLogListView(ListView):
    model = LoginLog
    template_name = 'users/login_journal.html'
    context_object_name = 'logs'
    ordering = ['-timestamp']
    paginate_by = 30


def dashboard(request):
    total_tasks = Task.objects.count()
    urgent_tasks = Task.objects.filter(deadline__lte=timezone.now() + timedelta(days=2), is_completed=False).count()

    documents_pending = Document.objects.filter(status='на согласовании').count()
    documents_returned = Document.objects.filter(status='на доработке').count()

    context = {
        'total_tasks': total_tasks,
        'urgent_tasks': urgent_tasks,
        'documents_pending': documents_pending,
        'documents_returned': documents_returned,
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
    documents = Document.objects.filter(status='на согласовании')
    return render(request, 'users/review_list.html', {'documents': documents})

@login_required
def review_document(request, doc_id):
    document = get_object_or_404(Document, pk=doc_id)
    if request.method == 'POST':
        form = DocumentReviewForm(request.POST, instance=document)
        if form.is_valid():
            form.save()
            return redirect('documents_for_review')
    else:
        form = DocumentReviewForm(instance=document)
    return render(request, 'users/review_form.html', {'form': form, 'document': document})


@login_required
def archive_view(request):
    documents = Document.objects.exclude(status='на согласовании').order_by('-created_at')
    return render(request, 'users/archive.html', {'documents': documents})


@login_required
def create_document(request):
    if request.method == 'POST':
        form = DocumentCreateForm(request.POST, request.FILES)
        if form.is_valid():
            document = form.save(commit=False)
            # статус автоматически будет 'на согласовании'
            document.save()
            return redirect('documents_for_review') 
    else:
        form = DocumentCreateForm()
    return render(request, 'users/create_document.html', {'form': form})