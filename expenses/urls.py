from django.urls import path

from . import views


urlpatterns = [

    # =========================================
    # COMPANY EXPENSES
    # =========================================

    path(
        "company/",
        views.company_expense_list,
        name="company_expense_list"
    ),

    path(
        "company/add/",
        views.company_expense_create,
        name="company_expense_create"
    ),

    path(
        "company/<int:pk>/edit/",
        views.company_expense_edit,
        name="company_expense_edit"
    ),

    path(
        "company/<int:pk>/delete/",
        views.company_expense_delete,
        name="company_expense_delete"
    ),

    path(
        "company/report/",
        views.company_expense_report,
        name="company_expense_report"
    ),


    # =========================================
    # DEALER EXPENSES
    # =========================================

    path(
        "dealer/",
        views.dealer_expense_list,
        name="dealer_expense_list"
    ),

    path(
        "dealer/add/",
        views.dealer_expense_create,
        name="dealer_expense_create"
    ),

    path(
        "dealer/<int:pk>/edit/",
        views.dealer_expense_edit,
        name="dealer_expense_edit"
    ),

    path(
        "dealer/<int:pk>/delete/",
        views.dealer_expense_delete,
        name="dealer_expense_delete"
    ),

    path(
        "dealer/report/",
        views.dealer_expense_report,
        name="dealer_expense_report"
    ),
]