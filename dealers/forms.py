from django import forms
from .models import Dealer


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