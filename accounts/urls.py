from django.urls import path
from .views import user_login, staff_list, staff_create,user_logout,dealer_admin_create,dealer_admin_list,permission_assign,permission_list

urlpatterns = [
    path('', user_login, name='login'),
    path('staff/',staff_list,name='staff_list'),
    path('staff/create/',staff_create,name='staff_create'),
    path('logout/',user_logout,name='logout'),
    path('dealer-admins/', dealer_admin_list, name='dealer_admin_list'),
    path('dealer-admins/create/', dealer_admin_create, name='dealer_admin_create'),
     path(
        'permissions/',
        permission_list,
        name='permission_list'
    ),

    path(
        'permissions/assign/',
        permission_assign,
        name='permission_assign'
    ),
    
]