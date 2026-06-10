from django.urls import path
from .views import (
    super_dashboard,
    dealer_dashboard,
    staff_dashboard,
    dealer_staff_dashboard
)

urlpatterns = [

    path(
        'super/',
        super_dashboard,
        name='super_dashboard'
    ),

    path(
        'dealer/',
        dealer_dashboard,
        name='dealer_dashboard'
    ),

    path(
        'staff/',
        staff_dashboard,
        name='staff_dashboard'
    ),

    path(
        'dealer-staff/',
        dealer_staff_dashboard,
        name='dealer_staff_dashboard'
    ),

]