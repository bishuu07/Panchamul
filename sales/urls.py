from django.urls import path
from . import views

urlpatterns = [

    path(
        'customers/',
        views.customer_list,
        name='customer_list'
    ),

    path(
        'customers/create/',
        views.customer_create,
        name='customer_create'
    ),

    path(
        'customers/edit/<int:pk>/',
        views.customer_edit,
        name='customer_edit'
    ),

    path(
    'sales/',
    views.sale_list,
    name='sale_list'
    ),

    path(
    'sales/create/',
    views.sale_create,
    name='sale_create'
    ),  


    path(
    'customer-payments/',
    views.customer_payment_list,
    name='customer_payment_list'
),

path(
    'customer-payments/create/',
    views.customer_payment_create,
    name='customer_payment_create'
),

path(
    'customer-ledgers/',
    views.customer_ledger_list,
    name='customer_ledger_list'
),

path(
    'customer-ledgers/<int:customer_id>/',
    views.customer_ledger_detail,
    name='customer_ledger_detail'
),

path(
    'customer-outstanding/',
    views.customer_outstanding_report,
    name='customer_outstanding_report'
),

path(
    'sales-returns/',
    views.sales_return_list,
    name='sales_return_list'
),

path(
    'sales-returns/create/',
    views.sales_return_create,
    name='sales_return_create'
),

path(
    'sales-items/<int:sale_id>/',
    views.sale_items_json,
    name='sale_items_json'
),
]