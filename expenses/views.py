from decimal import Decimal

from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.shortcuts import (
    get_object_or_404,
    redirect,
    render,
)

from .forms import (
    CompanyExpenseForm,
    DealerExpenseForm,
)

from .models import (
    CompanyExpense,
    DealerExpense,
)



@login_required
def company_expense_list(request):

    expenses = (
        CompanyExpense.objects
        .select_related(
            "created_by",
            "vehicle"
        )
        .order_by("-expense_date", "-id")
    )

    total = expenses.aggregate(
        total=Sum("amount")
    )["total"] or Decimal("0")

    return render(
        request,
        "expenses/company/company_expense_list.html",
        {
            "expenses": expenses,
            "total": total,
        }
    )


@login_required
def company_expense_create(request):

    if request.method == "POST":

        form = CompanyExpenseForm(request.POST)

        if form.is_valid():

            expense = form.save(
                commit=False
            )

            expense.created_by = request.user

            expense.save()

            return redirect(
                "company_expense_list"
            )

    else:

        form = CompanyExpenseForm()

    return render(
        request,
        "expenses/company/company_expense_form.html",
        {
            "form": form,
            "title": "Add Company Expense",
        }
    )


@login_required
def company_expense_edit(request, pk):

    expense = get_object_or_404(
        CompanyExpense,
        pk=pk
    )

    if request.method == "POST":

        form = CompanyExpenseForm(
            request.POST,
            instance=expense
        )

        if form.is_valid():

            form.save()

            return redirect(
                "company_expense_list"
            )

    else:

        form = CompanyExpenseForm(
            instance=expense
        )

    return render(
        request,
        "expenses/company/company_expense_form.html",
        {
            "form": form,
            "title": "Edit Company Expense",
        }
    )


@login_required
def company_expense_delete(request, pk):

    expense = get_object_or_404(
        CompanyExpense,
        pk=pk
    )

    if request.method == "POST":

        expense.delete()

        return redirect(
            "company_expense_list"
        )

    return render(
        request,
        "expenses/company/company_expense_confirm_delete.html",
        {
            "expense": expense
        }
    )


@login_required
def company_expense_report(request):

    expenses = (
        CompanyExpense.objects
        .select_related(
            "vehicle",
            "created_by"
        )
        .order_by(
            "-expense_date",
            "-id"
        )
    )

    total = expenses.aggregate(
        total=Sum("amount")
    )["total"] or Decimal("0")

    category_totals = (
        expenses
        .values("category")
        .annotate(
            total=Sum("amount")
        )
        .order_by("-total")
    )

    return render(
        request,
        "expenses/company/company_expense_report.html",
        {
            "expenses": expenses,
            "total": total,
            "category_totals": category_totals,
        }
    )



#dealer expenses view
from dealers.models import Dealer
from dealers.models import DealerProfile
@login_required
def dealer_expense_list(request):

    profile = get_object_or_404(
        DealerProfile,
        admin_user=request.user
    )

    dealer = profile.dealer

    expenses = (
        DealerExpense.objects
        .filter(dealer=dealer)
        .select_related("created_by")
        .order_by(
            "-expense_date",
            "-id"
        )
    )

    total = expenses.aggregate(
        total=Sum("amount")
    )["total"] or Decimal("0")

    return render(
        request,
        "expenses/dealer_portal/dealer_expense_list.html",
        {
            "expenses": expenses,
            "total": total,
        }
    )


@login_required
def dealer_expense_create(request):

    profile = get_object_or_404(
        DealerProfile,
        admin_user=request.user
    )

    dealer = profile.dealer

    if request.method == "POST":

        form = DealerExpenseForm(
            request.POST
        )

        if form.is_valid():

            expense = form.save(
                commit=False
            )

            expense.dealer = dealer

            expense.created_by = request.user

            expense.save()

            return redirect(
                "dealer_expense_list"
            )

    else:

        form = DealerExpenseForm()

    return render(
        request,
        "expenses/dealer_portal/dealer_expense_form.html",
        {
            "form": form,
            "title": "Add Dealer Expense",
        }
    )


@login_required
def dealer_expense_edit(request, pk):

    profile = get_object_or_404(
        DealerProfile,
        admin_user=request.user
    )

    expense = get_object_or_404(
        DealerExpense,
        pk=pk,
        dealer=profile.dealer
    )

    if request.method == "POST":

        form = DealerExpenseForm(
            request.POST,
            instance=expense
        )

        if form.is_valid():

            form.save()

            return redirect(
                "dealer_expense_list"
            )

    else:

        form = DealerExpenseForm(
            instance=expense
        )

    return render(
        request,
        "expenses/dealer_portal/dealer_expense_form.html",
        {
            "form": form,
            "title": "Edit Dealer Expense",
        }
    )


@login_required
def dealer_expense_delete(request, pk):

    profile = get_object_or_404(
        DealerProfile,
        admin_user=request.user
    )

    expense = get_object_or_404(
        DealerExpense,
        pk=pk,
        dealer=profile.dealer
    )

    if request.method == "POST":

        expense.delete()

        return redirect(
            "dealer_expense_list"
        )

    return render(
        request,
        "expenses/dealer_portal/dealer_expense_confirm_delete.html",
        {
            "expense": expense
        }
    )


@login_required
def dealer_expense_report(request):

    profile = get_object_or_404(
        DealerProfile,
        admin_user=request.user
    )

    dealer = profile.dealer

    expenses = (
        DealerExpense.objects
        .filter(dealer=dealer)
        .select_related("created_by")
        .order_by(
            "-expense_date",
            "-id"
        )
    )

    total = expenses.aggregate(
        total=Sum("amount")
    )["total"] or Decimal("0")

    category_totals = (
        expenses
        .values("category")
        .annotate(
            total=Sum("amount")
        )
        .order_by("-total")
    )

    return render(
        request,
        "expenses/dealer_portal/dealer_expense_report.html",
        {
            "expenses": expenses,
            "total": total,
            "category_totals": category_totals,
        }
    )