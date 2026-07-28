from django.urls import path
from .views import (
    dealer_list,
    dealer_create,
    dealer_edit,
    dealer_toggle_status,
    dealer_delete,
    dealer_return_create,
    dealer_outstanding_report,
  
    
)
from . import views
urlpatterns = [

    path(
        '',
        dealer_list,
        name='dealer_list'
    ),

    path(
        'create/',
        dealer_create,
        name='dealer_create'
    ),
    path('edit/<int:pk>/', dealer_edit, name='dealer_edit'),
    path('toggle/<int:pk>/', dealer_toggle_status, name='dealer_toggle_status'),
    path(
    'delete/<int:pk>/',
    dealer_delete,
    name='dealer_delete'
),
    path(
    'ledger/<int:dealer_id>/',
    views.dealer_ledger,
    name='dealer_ledger'
),

path(
    'payments/',
    views.dealer_payment_list,
    name='dealer_payment_list'
),

path(
    'payments/create/',
    views.dealer_payment_create,
    name='dealer_payment_create'
),
path(
    'outstanding/',
    views.dealer_outstanding_report,
    name='dealer_outstanding_report'
),

path(
    'outstanding-report/',
    dealer_outstanding_report,
    name='dealer_outstanding_report'
),
path('dealer-returns/create/', dealer_return_create, name='dealer_return_create'),

]