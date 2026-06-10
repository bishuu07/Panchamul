from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from dealers.models import Dealer
from accounts.models import User,ModulePermission



@login_required
def super_dashboard(request):

    if request.user.role != 'SUPER_ADMIN':
        return redirect('login')

    context = {

        'total_dealers':
            Dealer.objects.count(),

        'total_dealer_admins':
            User.objects.filter(
                role='DEALER_ADMIN'
            ).count(),

        'total_staff':
            User.objects.filter(
                role='COMPANY_STAFF'
            ).count(),

        'total_products':
            0,
    }

    return render(
        request,
        'dashboard/super_admin/dashboard.html',
        context
    )


@login_required
def dealer_dashboard(request):

    return render(
        request,
        'dashboard/dealer/dashboard.html'
    )


@login_required
def staff_dashboard(request):

    permissions = ModulePermission.objects.filter(
        user=request.user,
        can_view=True
    )

    return render(
        request,
        'dashboard/staff/dashboard.html',
        {
            'permissions': permissions
        }
    )

@login_required
def dealer_staff_dashboard(request):

    return render(
        request,
        'dashboard/dealer_staff/dashboard.html'
    )

