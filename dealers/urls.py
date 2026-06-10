from django.urls import path
from .views import (
    dealer_list,
    dealer_create,
    dealer_edit,
    dealer_toggle_status,
    dealer_delete,
)

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

]