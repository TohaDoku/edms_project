from django.urls import path
from .views import *
from django.views.generic import TemplateView

urlpatterns = [
    path('incoming/add/', add_incoming_document, name='incoming_add'),
    path('incoming/success/', TemplateView.as_view(template_name='documents/success.html'), name='incoming_success'),
    path('incoming/<int:doc_id>/assign/', assign_route, name='assign_route'),
    path('routes/', RouteListView.as_view(), name='route_list'),

    path('outgoing/create/', create_outgoing_document, name='create_outgoing'),
    path('outgoing/success/', TemplateView.as_view(template_name='documents/success_outgoing.html'), name='outgoing_success'),

    path('archive/', document_archive, name='document_archive'),
]
