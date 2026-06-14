from django.urls import path
from .views import(
    raw_material_create, raw_material_edit, raw_material_list, supplier_create, supplier_delete,raw_material_delete, supplier_edit,supplier_list,purchase_list,purchase_create
)
from . import views


urlpatterns = [
    path(
    'raw-materials/',
    raw_material_list,
    name='raw_material_list'
),

path(
    'raw-materials/create/',
    raw_material_create,
    name='raw_material_create'
),

path(
    'raw-materials/edit/<int:pk>/',
    raw_material_edit,
    name='raw_material_edit'
),
path(
    'raw-materials/delete/<int:pk>/',
    raw_material_delete,
    name='raw_material_delete'
),
path(
        'suppliers/',
        supplier_list,
        name='supplier_list'
    ),

    path(
        'suppliers/create/',
        supplier_create,
        name='supplier_create'
    ),

    path(
        'suppliers/edit/<int:pk>/',
        supplier_edit,
        name='supplier_edit'
    ),

    path(
        'suppliers/delete/<int:pk>/',
        supplier_delete,
        name='supplier_delete'
    ),

    path(
        'purchases/',
        purchase_list,
        name='purchase_list'
    ),

    path(
        'purchases/create/',
        purchase_create,
        name='purchase_create'
    ),

    path(
        'issues/',
        views.issue_list,
        name='issue_list'
    ),

    path(
        'issues/create/',
        views.issue_create,
        name='issue_create'
    ),
    path(
        'returns/',
        views.return_list,
        name='return_list'
    ),

    path(
        'returns/create/',
        views.return_create,
        name='return_create'
    ),
    path(
    'productions/',
    views.production_list,
    name='production_list'
    ),

    path(
    'productions/create/',
    views.production_create,
    name='production_create'
    ),

    path(
    'products/',
    views.product_list,
    name='product_list'
    ),

    path(
    'products/create/',
    views.product_create,
    name='product_create'
    ),

    path(
    'finished-stock/',
    views.finished_stock_list,
    name='finished_stock_list'
    ),
    path(
        'dealer-stock/',
        views.dealer_stock_list,
        name='dealer_stock_list'
    ),

    path(
    'dispatches/',
    views.dispatch_list,
    name='dispatch_list'
    ),

    path(
        'dispatches/create/',
        views.dispatch_create,
        name='dispatch_create'
    ),
    path(
    'dispatches/<int:pk>/',
    views.dispatch_detail,
    name='dispatch_detail'
),
]