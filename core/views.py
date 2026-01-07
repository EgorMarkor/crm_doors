from datetime import timedelta

from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from core.models import DeliveryRequest, InstallationRequest, User


@login_required
def dashboard(request: HttpRequest) -> HttpResponse:
    user: User = request.user
    now = timezone.now()
    upcoming_installations = (
        InstallationRequest.objects.filter(scheduled_for__gte=now).order_by('scheduled_for')[:5]
    )
    upcoming_deliveries = (
        DeliveryRequest.objects.filter(scheduled_for__gte=now).order_by('scheduled_for')[:5]
    )
    context = {
        'upcoming_installations': upcoming_installations,
        'upcoming_deliveries': upcoming_deliveries,
        'soon_window': now + timedelta(days=7),
    }
    if user.is_owner():
        return render(request, 'core/dashboard_owner.html', context)
    if user.is_manager():
        return render(request, 'core/dashboard_manager.html', context)
    if user.is_installer():
        my_installations = InstallationRequest.objects.filter(installer=user).order_by('scheduled_for')[:5]
        context.update({'my_installations': my_installations})
        return render(request, 'core/dashboard_installer.html', context)
    if user.is_delivery():
        my_deliveries = DeliveryRequest.objects.filter(courier=user).order_by('scheduled_for')[:5]
        context.update({'my_deliveries': my_deliveries})
        return render(request, 'core/dashboard_delivery.html', context)
    return render(request, 'core/dashboard_owner.html', context)


@login_required
def installation_requests(request: HttpRequest) -> HttpResponse:
    user: User = request.user
    if user.is_manager():
        qs = InstallationRequest.objects.filter(manager=user)
    elif user.is_installer():
        qs = InstallationRequest.objects.filter(installer=user)
    else:
        qs = InstallationRequest.objects.all()
    return render(request, 'core/installation_requests.html', {'requests': qs})


@login_required
def delivery_requests(request: HttpRequest) -> HttpResponse:
    user: User = request.user
    if user.is_manager():
        qs = DeliveryRequest.objects.filter(manager=user)
    elif user.is_delivery():
        qs = DeliveryRequest.objects.filter(courier=user)
    else:
        qs = DeliveryRequest.objects.all()
    return render(request, 'core/delivery_requests.html', {'requests': qs})


@login_required
def free_installation_requests(request: HttpRequest) -> HttpResponse:
    qs = InstallationRequest.objects.filter(installer__isnull=True)
    return render(request, 'core/free_requests.html', {'requests': qs, 'type': 'installation'})


@login_required
def free_delivery_requests(request: HttpRequest) -> HttpResponse:
    qs = DeliveryRequest.objects.filter(courier__isnull=True)
    return render(request, 'core/free_requests.html', {'requests': qs, 'type': 'delivery'})


@login_required
def claim_installation(request: HttpRequest, request_id: int) -> HttpResponse:
    user: User = request.user
    if not user.is_installer():
        return redirect('free_installation_requests')
    installation_request = get_object_or_404(InstallationRequest, pk=request_id, installer__isnull=True)
    installation_request.installer = user
    installation_request.status = 'Назначен установщик'
    installation_request.save()
    return redirect('installation_requests')


@login_required
def claim_delivery(request: HttpRequest, request_id: int) -> HttpResponse:
    user: User = request.user
    if not user.is_delivery():
        return redirect('free_delivery_requests')
    delivery_request = get_object_or_404(DeliveryRequest, pk=request_id, courier__isnull=True)
    delivery_request.courier = user
    delivery_request.status = 'Назначен доставщик'
    delivery_request.save()
    return redirect('delivery_requests')


@login_required
def placeholder_section(request: HttpRequest, section: str) -> HttpResponse:
    return render(request, 'core/placeholder_section.html', {'section': section})
