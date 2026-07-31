from django.urls import path
from .views import (
    super_dashboard,
    dealer_dashboard,
    staff_dashboard,
    dealer_staff_dashboard
)
from . import views

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
    path(
        "super/dealer/<int:pk>/",
        views.super_dealer_dashboard,
        name="super_dealer_dashboard",
    ),
   path(
    "super/dealer/<int:pk>/statement/",
    views.super_dealer_statement,
    name="super_dealer_statement",
),
path(
    "super/dealer/<int:pk>/statement/report/",
    views.super_dealer_statement_report,
    name="super_dealer_statement_report",
),
]