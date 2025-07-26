from django.urls import path
from .views import *
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('', CustomLoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),
    path('login-journal/', LoginLogListView.as_view(), name='login_journal'),

    path('dashboard/', dashboard, name='dashboard'),
]
