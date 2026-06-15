from django import forms
from .models import RawMaterial, Supplier, RawMaterialPurchase,MaterialIssue,Product,Production,Dispatch


class RawMaterialForm(forms.ModelForm):

    class Meta:

        model = RawMaterial

        fields = [
            'name',
            'unit',
            'minimum_stock',
            'is_active'
        ]





class SupplierForm(forms.ModelForm):

    class Meta:

        model = Supplier

        fields = [
            'name',
            'phone',
            'email',
            'address',
            'is_active'
        ]

class RawMaterialPurchaseForm(forms.ModelForm):

    class Meta:

        model = RawMaterialPurchase

        fields = [
            'supplier',
            'invoice_number',
            'purchase_date',
            'remarks'
        ]

        widgets = {
            'purchase_date': forms.DateInput(
                attrs={
                    'type': 'date'
                }
            )
        }


class MaterialIssueForm(forms.ModelForm):

    class Meta:

        model = MaterialIssue

        fields = [
            'issue_date',
            'remarks'
        ]


class ProductForm(forms.ModelForm):

    class Meta:

        model = Product

        fields = [
            'name',
            # 'sku',
            'unit',
            'minimum_stock',
            
            'is_active'
        ]

class ProductionForm(forms.ModelForm):

    class Meta:

        model = Production

        fields = [
            'batch_number',
            'production_date',
            'remarks'
        ]

        widgets = {
            'production_date': forms.DateInput(
                attrs={'type': 'date'}
            )
        }


class DispatchForm(forms.ModelForm):

    class Meta:

        model = Dispatch

        fields = [
            'dealer',
            'dispatch_no',
            'dispatch_date',
            'remarks'
        ]

        widgets = {
            'dispatch_date': forms.DateInput(
                attrs={
                    'type': 'date'
                }
            )
        }