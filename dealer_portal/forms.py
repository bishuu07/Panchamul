from django import forms
from .models import DealerCustomer,DealerSale,DealerSponsor


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