from django.urls import path
from .views import *
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('', CustomLoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),
    path('login-journal/', LoginLogListView.as_view(), name='login_journal'),

    path('dashboard/', dashboard, name='dashboard'),

    path('tasks/create/', create_task, name='create_task'),
    path('tasks/', task_list, name='task_list'),
    path('tasks/<int:task_id>/complete/', complete_task, name='complete_task'),
    path('tasks/<int:task_id>/edit/', edit_task, name='edit_task'),

    path('review/', documents_for_review, name='documents_for_review'),
    path('review/<int:doc_id>/', review_document, name='review_document'),
    path('archive/', archive_view, name='archive'),
    path('create/', create_document, name='create_document'),
    path('document/<int:document_id>/', document_detail, name='document_detail'),

    path('staff_structure_view/', staff_structure_view, name='staff_structure_view'),

    path('documents_for_update/', documents_for_update, name='documents_for_update'),

    path('documents/<int:document_id>/change-executor/', change_document_executor, name='change_document_executor'),

]
