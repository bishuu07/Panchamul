from django.urls import path
from .views import *
from . import views

urlpatterns = [

    path(
        '',
        dealer_home,
        name='dealer_home'
    ),

    path(
    'stock/',
    dealer_stock_list,
    name='dealer_stock_list'
),
path(
        'customers/',
        dealer_customer_list,
        name='dealer_customer_list'
    ),

    path(
        'customers/create/',
        dealer_customer_create,
        name='dealer_customer_create'
    ),
    # path(
    # 'dispatch/pending/',
    # dealer_pending_dispatch_list,
    # name='dealer_pending_dispatch_list'
    # ),

    path(
    'dispatch/approve/<int:pk>/',
    dealer_dispatch_approve,
    name='dealer_dispatch_approval'
),

path(
    'dispatch/edit/<int:pk>/',
    dealer_dispatch_edit,
    name='dealer_dispatch_edit'
),
    path(
    'dispatches/',
    dealer_dispatch_list,
    name='dealer_dispatch_list'
    ),

    path(
    'sales/',
    dealer_sale_list,
    name='dealer_sale_list'
),

path(
    'sales/create/',
    dealer_sale_create,
    name='dealer_sale_create'
),

path(
    'sales-return/',
    dealer_sales_return_list,
    name='dealer_sales_return_list'
),

path(
    'sales-return/create/',
    dealer_sales_return_create,
    name='dealer_sales_return_create'
),

path(
    'customer-payments/',
    dealer_customer_payment_list,
    name='dealer_customer_payment_list'
),

path(
    'customer-payments/create/',
    dealer_customer_payment_create,
    name='dealer_customer_payment_create'
),

path(
    'customer-ledger/',
    dealer_customer_ledger_list,
    name='dealer_customer_ledger_list'
),

path(
    'customer-ledger/<int:customer_id>/',
    dealer_customer_ledger_detail,
    name='dealer_customer_ledger_detail'
),

# path(
#     'outstanding-report/',
#     dealer_outstanding_report,
#     name='dealer_outstanding_report'
# ),

path(
    'vehicles/',
    vehicle_list,
    name='vehicle_list'
),

path(
    'vehicles/create/',
    vehicle_create,
    name='vehicle_create'
),

path(
    'vehicle-dispatches/',
    vehicle_dispatch_list,
    name='vehicle_dispatch_list'
),

path(
    'vehicle-dispatch/create/',
    vehicle_dispatch_create,
    name='vehicle_dispatch_create'
),

path(
    'vehicle-dispatch/close/<int:pk>/',
    vehicle_dispatch_close,
    name='vehicle_dispatch_close'
),


path(
    'vehicles/',
    vehicle_list,
    name='vehicle_list'
),

path(
    'vehicles/create/',
    vehicle_create,
    name='vehicle_create'
),
path(
    'sponsors/',
    sponsor_list,
    name='sponsor_list'
),

path(
    'sponsors/create/',
    sponsor_create,
    name='sponsor_create'
),
path(
    'reports/sales/',
    dealer_sales_report,
    name='dealer_sales_report'
),
path(
    'reports/stock/',
    dealer_stock_report,
    name='dealer_stock_report'
),
path(
    "vehicle-dispatch/<int:pk>/",
    views.vehicle_dispatch_detail,
    name="vehicle_dispatch_detail",
),
path(
    "vehicle-dispatch/<int:dispatch_id>/trip/create/",
    views.vehicle_trip_create,
    name="vehicle_trip_create",
),

path(
    "vehicle-trip/<int:trip_id>/close/",
    views.vehicle_trip_close,
    name="vehicle_trip_close",
),
path(
    "vehicle-dispatch/<int:pk>/report/",
    views.vehicle_dispatch_report,
    name="vehicle_dispatch_report",
),
path(
    "vehicle-trip/<int:trip_id>/",
    views.vehicle_trip_detail,
    name="vehicle_trip_detail",
),

]