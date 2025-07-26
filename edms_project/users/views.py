from django.contrib.auth.views import LoginView
from django.views.generic import ListView
from django.contrib.auth.decorators import user_passes_test
from django.utils.decorators import method_decorator
from .models import LoginLog
from django.shortcuts import render

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

    return render(request, 'users/dashboard.html')
