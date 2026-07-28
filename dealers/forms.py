from django import forms
from .models import Dealer, DealerPayment


class DealerForm(forms.ModelForm):

    class Meta:
        model = Dealer

        fields = [
            'name',
            'address',
            'phone',
            'email',
            'is_active'
        ]


class DealerPaymentForm(forms.ModelForm):

    class Meta:

        model = DealerPayment

        fields = [
            'dealer',
            'payment_date',
            'amount',
            'payment_mode',
            'reference_no',
            'remarks'
        ]