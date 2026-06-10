from django.shortcuts import render, redirect, get_object_or_404
from .models import Dealer
from .forms import DealerForm
from django.http import HttpResponse
from accounts.utils import has_permission


def dealer_list(request):

    if not has_permission(
        request.user,
        'DEALER',
        'can_view'
    ):
        return HttpResponse(
            "Permission Denied"
        )

    dealers = Dealer.objects.all().order_by('-id')

    return render(
        request,
        'dashboard/super_admin/dealer_list.html',
        {
            'dealers': dealers
        }
    )


def dealer_create(request):

    if not has_permission(
        request.user,
        'DEALER',
        'can_add'
    ):
        return HttpResponse(
            "Permission Denied"
        )

    form = DealerForm(
        request.POST or None
    )

    if form.is_valid():

        dealer = form.save(
            commit=False
        )

        dealer.created_by = request.user

        dealer.save()

        return redirect(
            'dealer_list'
        )

    return render(
        request,
        'dashboard/super_admin/dealer_create.html',
        {
            'form': form
        }
    )

    return render(
        request,
        'dashboard/super_admin/dealer_create.html',
        {
            'form': form
        }
    )

def dealer_edit(request, pk):

    if not has_permission(
        request.user,
        'DEALER',
        'can_edit'
    ):
        return HttpResponse(
            "Permission Denied"
        )

    dealer = get_object_or_404(
        Dealer,
        pk=pk
    )

    form = DealerForm(
        request.POST or None,
        instance=dealer
    )

    if form.is_valid():

        form.save()

        return redirect(
            'dealer_list'
        )

    return render(
        request,
        'dashboard/super_admin/dealer_create.html',
        {
            'form': form
        }
    )

def dealer_delete(request, pk):

    if not has_permission(
        request.user,
        'DEALER',
        'can_delete'
    ):
        return HttpResponse(
            "Permission Denied"
        )

    dealer = get_object_or_404(
        Dealer,
        pk=pk
    )

    dealer.is_active = False

    dealer.save()

    return redirect(
        'dealer_list'
    )

def dealer_toggle_status(request, pk):

    dealer = get_object_or_404(
        Dealer,
        pk=pk
    )

    dealer.is_active = not dealer.is_active

    dealer.save()

    return redirect(
        'dealer_list'
    )