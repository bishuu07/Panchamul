from django import forms

from .models import (
    CompanyExpense,
    DealerExpense,
)


class CompanyExpenseForm(forms.ModelForm):

    class Meta:
        model = CompanyExpense

        fields = [
            "expense_date",
            "category",
            "vehicle",
            "description",
            "amount",
        ]

        widgets = {
            "expense_date": forms.DateInput(
                attrs={
                    "type": "date",
                    "class": "form-control"
                }
            ),

            "category": forms.Select(
                attrs={
                    "class": "form-control"
                }
            ),

            "vehicle": forms.Select(
                attrs={
                    "class": "form-control"
                }
            ),

            "description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3
                }
            ),

            "amount": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "step": "0.01",
                    "min": "0"
                }
            ),
        }


class DealerExpenseForm(forms.ModelForm):

    class Meta:
        model = DealerExpense

        fields = [
            "expense_date",
            "category",
            "description",
            "amount",
        ]

        widgets = {
            "expense_date": forms.DateInput(
                attrs={
                    "type": "date",
                    "class": "form-control"
                }
            ),

            "category": forms.Select(
                attrs={
                    "class": "form-control"
                }
            ),

            "description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3
                }
            ),

            "amount": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "step": "0.01",
                    "min": "0"
                }
            ),
        }