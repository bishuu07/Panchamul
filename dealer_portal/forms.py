from django import forms
from .models import DealerCustomer,DealerSale,DealerSponsor, CompanyPayment



class DealerCustomerForm(forms.ModelForm):

    class Meta:

        model = DealerCustomer

        fields = [
            'name',
            'phone',
            'email',
            'address',
            'opening_balance',
            'is_active'
        ]


class DealerSaleForm(forms.ModelForm):

    class Meta:

        model = DealerSale

        fields = [
            'customer',
            'invoice_no',
            'sale_date',
            'paid_amount'
        ]


from .models import DealerVehicle

class DealerVehicleForm(forms.ModelForm):

    class Meta:

        model = DealerVehicle

        fields = [
            'vehicle_no',
            'driver_name',
            'phone',
            'is_active'
        ]


class DealerSponsorForm(forms.ModelForm):

    class Meta:

        model = DealerSponsor

        fields = [

            'customer',

            'product',

            'quantity',

            'sponsor_date',

            'remarks'

        ]






class CompanyPaymentForm(forms.ModelForm):

    class Meta:
        model = CompanyPayment
        fields = [
            'payment_date',
            'amount',
            'payment_method',
            'reference_no',
            'remarks',
        ]

        widgets = {
            'payment_date': forms.DateInput(
                attrs={
                    'type': 'date',
                    'class': 'form-control'
                }
            ),

            'amount': forms.NumberInput(
                attrs={
                    'class': 'form-control',
                    'step': '0.01',
                    'min': '0.01'
                }
            ),

            'payment_method': forms.Select(
                attrs={
                    'class': 'form-select'
                }
            ),

            'reference_no': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'e.g. PAY-0001'
                }
            ),

            'remarks': forms.Textarea(
                attrs={
                    'class': 'form-control',
                    'rows': 3,
                    'placeholder': 'Payment remarks...'
                }
            ),
        }