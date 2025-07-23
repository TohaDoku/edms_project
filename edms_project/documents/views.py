from django.shortcuts import render, redirect
from .forms import *
from .models import *
from django.contrib.auth.decorators import login_required
from .utils import *
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import user_passes_test
from django.utils.decorators import method_decorator
from django.views.generic import ListView
from django.core.paginator import Paginator
from django.db.models import Q
from django.utils.timezone import now


@login_required
def add_incoming_document(request):
    if request.method == 'POST':
        form = IncomingDocumentForm(request.POST, request.FILES)
        if form.is_valid():
            doc = form.save(commit=False)
            doc.number = generate_document_number()
            doc.registered_by = request.user
            doc.save()
            return redirect('incoming_success')
    else:
        form = IncomingDocumentForm()
    return render(request, 'documents/add_incoming.html', {'form': form})


@login_required
def assign_route(request, doc_id):
    document = get_object_or_404(IncomingDocument, id=doc_id)

    if request.method == 'POST':
        form = DocumentRouteForm(request.POST)
        if form.is_valid():
            route = form.save(commit=False)
            route.document = document
            route.save()
            return redirect('route_list')
    else:
        form = DocumentRouteForm()

    return render(request, 'documents/assign_route.html', {
        'form': form,
        'document': document
    })


@method_decorator(user_passes_test(lambda u: u.is_superuser or u.groups.filter(name__in=['Руководитель']).exists()), name='dispatch')
class RouteListView(ListView):
    model = DocumentRoute
    template_name = 'documents/route_list.html'
    context_object_name = 'routes'
    paginate_by = 20
    ordering = ['-updated_at']


@login_required
def create_outgoing_document(request):
    if request.method == 'POST':
        form = OutgoingDocumentForm(request.POST, request.FILES)
        if form.is_valid():
            doc = form.save(commit=False)
            doc.number = generate_outgoing_number()
            doc.created_by = request.user
            doc.status = 'on_approval'  # Сразу отправляется на согласование
            doc.save()
            return redirect('outgoing_success')
    else:
        form = OutgoingDocumentForm()

    return render(request, 'documents/create_outgoing.html', {'form': form})


@login_required
def document_archive(request):
    query = request.GET.get('q', '')
    doc_type = request.GET.get('type', '')
    status = request.GET.get('status', '')
    date_from = request.GET.get('from', '')
    date_to = request.GET.get('to', '')

    # Получаем все документы
    incoming = IncomingDocument.objects.all()
    outgoing = OutgoingDocument.objects.all()

    # Поиск и фильтрация
    if query:
        incoming = incoming.filter(Q(title__icontains=query) | Q(content__icontains=query) | Q(sender__icontains=query))
        outgoing = outgoing.filter(Q(title__icontains=query) | Q(content__icontains=query) | Q(recipient__icontains=query))

    if status:
        outgoing = outgoing.filter(status=status)

    if date_from:
        incoming = incoming.filter(received_date__gte=date_from)
        outgoing = outgoing.filter(created_at__gte=date_from)

    if date_to:
        incoming = incoming.filter(received_date__lte=date_to)
        outgoing = outgoing.filter(created_at__lte=date_to)

    # Добавляем тип и объединяем
    archive = [
        {"type": "Входящий", "number": d.number, "title": d.title, "date": d.received_date, "status": "—", "link": f"/documents/incoming/{d.id}/"}
        for d in incoming
    ] + [
        {"type": "Исходящий", "number": d.number, "title": d.title, "date": d.created_at, "status": d.get_status_display(), "link": f"/documents/outgoing/{d.id}/"}
        for d in outgoing
    ]

    archive.sort(key=lambda x: x['date'], reverse=True)

    paginator = Paginator(archive, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'documents/archive.html', {
        'documents': page_obj,
        'query': query,
        'doc_type': doc_type,
        'status': status,
        'date_from': date_from,
        'date_to': date_to,
        'page_obj': page_obj
    })