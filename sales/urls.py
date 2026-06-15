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
]