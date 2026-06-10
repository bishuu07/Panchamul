from django import forms
from .models import User
from dealers.models import Dealer


class StaffCreateForm(forms.ModelForm):

    password = forms.CharField(
        widget=forms.PasswordInput()
    )

    class Meta:
        model = User

        fields = [
            'first_name',
            'last_name',
            'username',
            'email',
            'phone',
            'password'
        ]

class DealerAdminCreateForm(forms.ModelForm):

    password = forms.CharField(
        widget=forms.PasswordInput()
    )

    dealer = forms.ModelChoiceField(
        queryset=Dealer.objects.filter(
            is_active=True
        )
    )

    class Meta:

        model = User

        fields = [
            'username',
            'first_name',
            'last_name',
            'email',
            'phone',
            'password'
        ]