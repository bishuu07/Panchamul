from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .forms import StaffCreateForm
from .models import User
from dealers.models import DealerProfile
from .forms import DealerAdminCreateForm
from django.contrib.auth.decorators import login_required




def user_login(request):

    print("VIEW CALLED")

    if request.method == 'POST':

        print("POST REQUEST RECEIVED")

        username = request.POST.get('username')
        password = request.POST.get('password')

        print("USERNAME:", username)

        user = authenticate(
            request,
            username=username,
            password=password
        )

        print("AUTH RESULT:", user)

        if user is not None:

            login(request, user)

            print("LOGIN SUCCESS")

            # SUPER ADMIN
            if user.role == 'SUPER_ADMIN':
                return redirect('super_dashboard')

            # COMPANY STAFF
            elif user.role == 'COMPANY_STAFF':
                return redirect('staff_dashboard')

            # DEALER ADMIN
            elif user.role == 'DEALER_ADMIN':
                return redirect('dealer_dashboard')

            # DEALER STAFF
            elif user.role == 'DEALER_STAFF':
                return redirect('dealer_staff_dashboard')

            # Fallback
            return redirect('login')

        else:

            print("LOGIN FAILED")

    return render(
        request,
        'accounts/login.html'
    )


def user_logout(request):

    logout(request)

    return redirect('login')

def staff_list(request):

    staffs = User.objects.filter(
        role='COMPANY_STAFF'
    )

    return render(
        request,
        'dashboard/super_admin/staff_list.html',
        {
            'staffs': staffs
        }
    )

def staff_create(request):

    form = StaffCreateForm(
        request.POST or None
    )

    if form.is_valid():

        user = form.save(
            commit=False
        )

        user.role = 'COMPANY_STAFF'

        user.set_password(
            form.cleaned_data['password']
        )

        user.save()

        return redirect(
            'staff_list'
        )

    return render(
        request,
        'dashboard/super_admin/staff_create.html',
        {
            'form': form
        }
    )

def dealer_admin_create(request):

    form = DealerAdminCreateForm(
        request.POST or None
    )

    if form.is_valid():

        dealer = form.cleaned_data['dealer']

        user = form.save(
            commit=False
        )

        user.role = 'DEALER_ADMIN'

        user.set_password(
            form.cleaned_data['password']
        )

        user.save()

        DealerProfile.objects.create(

            dealer=dealer,

            admin_user=user

        )

        return redirect(
            'dealer_admin_list'
        )

    return render(
        request,
        'dashboard/super_admin/dealer_admin_create.html',
        {
            'form': form
        }
    )
def dealer_admin_list(request):

    dealer_admins = User.objects.filter(
        role='DEALER_ADMIN'
    )

    return render(
        request,
        'dashboard/super_admin/dealer_admin_list.html',
        {
            'dealer_admins': dealer_admins
        }
    )

from .models import User, ModulePermission
@login_required
def permission_assign(request):

    users = User.objects.exclude(
        role='SUPER_ADMIN'
    )

    modules = [
        'DEALER',
        'PRODUCT',
        'STOCK',
        'DISPATCH',
        'SALES',
        'PAYMENT',
        'REPORT'
    ]

    if request.method == 'POST':

        user_id = request.POST.get('user')

        selected_user = User.objects.get(
            id=user_id
        )

        ModulePermission.objects.filter(
            user=selected_user
        ).delete()

        for module in modules:

            ModulePermission.objects.create(

                user=selected_user,

                module=module,

                can_view=bool(
                    request.POST.get(
                        f'{module}_view'
                    )
                ),

                can_add=bool(
                    request.POST.get(
                        f'{module}_add'
                    )
                ),

                can_edit=bool(
                    request.POST.get(
                        f'{module}_edit'
                    )
                ),

                can_delete=bool(
                    request.POST.get(
                        f'{module}_delete'
                    )
                )
            )

        return redirect(
            'permission_list'
        )

    return render(
        request,
        'dashboard/super_admin/permission_assign.html',
        {
            'users': users,
            'modules': modules
        }
    )

@login_required
def permission_list(request):

    permissions = ModulePermission.objects.select_related(
        'user'
    )

    return render(
        request,
        'dashboard/super_admin/permission_list.html',
        {
            'permissions': permissions
        }
    )