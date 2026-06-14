from django.shortcuts import render, redirect, get_object_or_404
from .models import RawMaterial,Supplier
from .forms import MaterialIssueForm, RawMaterialForm,SupplierForm, ProductForm,ProductionForm
from django.contrib.auth.decorators import login_required
from .models import (
    RawMaterial,
    RawMaterialPurchase,
    RawMaterialPurchaseItem,
    MaterialIssue,
    MaterialIssueItem,
    RawMaterial,
    Production,
    Product,
    ProductionItem,
    DealerStock,
    Dispatch,
    DispatchItem,
    Product,
   
)
from django.db.models import F

from .forms import (
    RawMaterialPurchaseForm,DispatchForm
)
from django.http import JsonResponse
import json
from decimal import Decimal


def raw_material_list(request):

    materials = RawMaterial.objects.all().order_by('-id')

    return render(
        request,
        'inventory/raw_material_list.html',
        {
            'materials': materials
        }
    )
def raw_material_create(request):

    form = RawMaterialForm(
        request.POST or None
    )

    if form.is_valid():

        form.save()

        return redirect(
            'raw_material_list'
        )

    return render(
        request,
        'inventory/raw_material_create.html',
        {
            'form': form
        }
    )

def raw_material_edit(request, pk):

    material = get_object_or_404(
        RawMaterial,
        pk=pk
    )

    form = RawMaterialForm(
        request.POST or None,
        instance=material
    )

    if form.is_valid():

        form.save()

        return redirect(
            'raw_material_list'
        )

    return render(
        request,
        'inventory/raw_material_create.html',
        {
            'form': form
        }
    )


def raw_material_delete(request, pk):

    material = get_object_or_404(
        RawMaterial,
        pk=pk
    )

    material.delete()

    return redirect(
        'raw_material_list'
    )

def supplier_list(request):

    suppliers = Supplier.objects.all().order_by('-id')

    return render(
        request,
        'inventory/supplier_list.html',
        {
            'suppliers': suppliers
        }
    )

def supplier_create(request):

    form = SupplierForm(
        request.POST or None
    )

    if form.is_valid():

        form.save()

        return redirect(
            'supplier_list'
        )

    return render(
        request,
        'inventory/supplier_create.html',
        {
            'form': form
        }
    )

def supplier_edit(request, pk):

    supplier = get_object_or_404(
        Supplier,
        pk=pk
    )

    form = SupplierForm(
        request.POST or None,
        instance=supplier
    )

    if form.is_valid():

        form.save()

        return redirect(
            'supplier_list'
        )

    return render(
        request,
        'inventory/supplier_create.html',
        {
            'form': form
        }
    )

def supplier_delete(request, pk):

    supplier = get_object_or_404(
        Supplier,
        pk=pk
    )

    supplier.delete()

    return redirect(
        'supplier_list'
    )

def purchase_create(request):

    form = RawMaterialPurchaseForm(
        request.POST or None
    )

    materials = RawMaterial.objects.filter(
        is_active=True
    )

    if request.method == 'POST':

        if form.is_valid():

            purchase = form.save(
                commit=False
            )

            purchase.created_by = request.user

            purchase.save()

            items = json.loads(
                request.POST.get(
                    'items_json'
                )
            )

            for item in items:

                material = RawMaterial.objects.get(
                    id=item['material']
                )

                qty = Decimal(
                    str(item['quantity'])
                )

                rate = Decimal(
                    str(item['rate'])
                )

                RawMaterialPurchaseItem.objects.create(
                    purchase=purchase,
                    raw_material=material,
                    quantity=qty,
                    rate=rate,
                    amount=qty * rate
                )

            return redirect(
                'purchase_list'
            )

    return render(
        request,
        'inventory/purchase_create.html',
        {
            'form': form,
            'materials': materials
        }
    )

def purchase_list(request):

    purchases = RawMaterialPurchase.objects.all().order_by(
        '-id'
    )

    return render(
        request,
        'inventory/purchase_list.html',
        {
            'purchases': purchases
        }
    )

def issue_create(request):

    form = MaterialIssueForm(
        request.POST or None
    )

    materials = RawMaterial.objects.filter(
        is_active=True
    )

    if request.method == 'POST':

        if form.is_valid():

            items_json = request.POST.get(
                'items_json',
                '[]'
            )

            if not items_json:

                return render(
                    request,
                    'inventory/issue_create.html',
                    {
                        'form': form,
                        'materials': materials,
                        'error':
                            'Please add at least one material.'
                    }
                )

            items = json.loads(
                items_json
            )

            issue = form.save(
                commit=False
            )

            issue.created_by = request.user

            issue.save()

            for item in items:

                material = RawMaterial.objects.get(
                    id=item['material']
                )

                qty = Decimal(
                item['quantity']
                )

                if material.current_stock < qty:

                    return render(
                        request,
                        'inventory/issue_create.html',
                        {
                            'form': form,
                            'materials': materials,
                            'error':
                                f'Not enough stock for {material.name}'
                        }
                    )

                MaterialIssueItem.objects.create(
                    issue=issue,
                    raw_material=material,
                    quantity=qty
                )

                material.current_stock -= qty
                material.save()

            return redirect(
                'issue_list'
            )

    return render(
        request,
        'inventory/issue_create.html',
        {
            'form': form,
            'materials': materials
        }
    )

def issue_list(request):

    issues = MaterialIssue.objects.prefetch_related(
        'items',
        'items__raw_material'
    ).order_by('-id')

    return render(
        request,
        'inventory/issue_list.html',
        {
            'issues': issues
        }
    )




def return_list(request):

    return render(
        request,
        'inventory/return_list.html'
    )


def return_create(request):

    return render(
        request,
        'inventory/return_create.html'
    )

@login_required
def production_list(request):

    productions = Production.objects.all().order_by(
        '-id'
    )

    return render(
        request,
        'inventory/production_list.html',
        {
            'productions': productions
        }
    )


@login_required
def product_create(request):

    form = ProductForm(
        request.POST or None
    )

    if form.is_valid():

        form.save()

        return redirect(
            'product_list'
        )

    return render(
        request,
        'inventory/product_create.html',
        {
            'form': form
        }
    )

@login_required
def product_list(request):

    products = Product.objects.all().order_by(
        '-id'
    )

    return render(
        request,
        'inventory/product_list.html',
        {
            'products': products
        }
    )



@login_required
def production_create(request):

    form = ProductionForm(
        request.POST or None
    )

    products = Product.objects.filter(
        is_active=True
    )

    if request.method == 'POST':

        if form.is_valid():

            production = form.save(
                commit=False
            )

            production.created_by = request.user

            production.save()

            items = json.loads(
                request.POST.get(
                    'items_json'
                )
            )

            for item in items:

                product = Product.objects.get(
                    id=item['product']
                )

                qty_produced = Decimal(
                    str(item['quantity_produced'])
                )

                qty_wasted = Decimal(
                    str(item['quantity_wasted'])
                )

                ProductionItem.objects.create(
                    production=production,
                    product=product,
                    quantity_produced=qty_produced,
                    quantity_wasted=qty_wasted
                )

            return redirect(
                'production_list'
            )

    return render(
        request,
        'inventory/production_create.html',
        {
            'form': form,
            'products': products
        }
    )

@login_required
def finished_stock_list(request):

    products = Product.objects.all().order_by(
        'name'
    )

    return render(
        request,
        'inventory/finished_stock_list.html',
        {
            'products': products
        }
    )

@login_required
def dealer_stock_list(request):

    stocks = DealerStock.objects.select_related(
        'dealer',
        'product'
    ).order_by(
        'dealer__name',
        'product__name'
    )

    return render(
        request,
        'inventory/dealer_stock_list.html',
        {
            'stocks': stocks
        }
    )



@login_required
def dispatch_create(request):

    form = DispatchForm(
        request.POST or None
    )

    products = Product.objects.filter(
        is_active=True
    )

    if request.method == 'POST':

        if form.is_valid():

            dispatch = form.save(
                commit=False
            )

            dispatch.created_by = request.user

            dispatch.save()

            items = json.loads(
                request.POST.get(
                    'items_json'
                )
            )

            for item in items:

                product = Product.objects.get(
                    id=item['product']
                )

                qty = Decimal(
                    str(item['quantity'])
                )

                # stock validation

                if product.current_stock < qty:

                    dispatch.delete()

                    return render(
                        request,
                        'inventory/dispatch_create.html',
                        {
                            'form': form,
                            'products': products,
                            'error': f'Not enough stock for {product.name}'
                        }
                    )

                DispatchItem.objects.create(
                    dispatch=dispatch,
                    product=product,
                    dispatched_qty=qty
                )

                product.current_stock -= qty

                product.save()

            return redirect(
                'dispatch_list'
            )

    return render(
        request,
        'inventory/dispatch_create.html',
        {
            'form': form,
            'products': products
        }
    )

@login_required
def dispatch_list(request):

    dispatches = Dispatch.objects.select_related(
        'dealer'
    ).order_by(
        '-id'
    )

    return render(
        request,
        'inventory/dispatch_list.html',
        {
            'dispatches': dispatches
        }
    )


@login_required
def dispatch_detail(request, pk):

    dispatch = get_object_or_404(
        Dispatch,
        pk=pk
    )

    if request.method == 'POST':

        items = request.POST.getlist('items[]')

        total_received = 0

        for item_id in items:

            item = DispatchItem.objects.get(id=item_id)

            received = Decimal(request.POST.get(f'received_{item_id}', 0))
            damaged = Decimal(request.POST.get(f'damaged_{item_id}', 0))
            returned = Decimal(request.POST.get(f'returned_{item_id}', 0))

            item.received_qty = received
            item.damaged_qty = damaged
            item.returned_qty = returned
            item.save()

            # Update dealer stock
            net_qty = received

            stock, created = DealerStock.objects.get_or_create(
                dealer=dispatch.dealer,
                product=item.product,
                defaults={
                    'quantity': 0
                }
            )

            stock.quantity += net_qty
            stock.save()

            total_received += received

        # update status
        if total_received == 0:
            dispatch.status = 'PENDING'
        elif total_received < sum(i.dispatched_qty for i in dispatch.items.all()):
            dispatch.status = 'PARTIAL'
        else:
            dispatch.status = 'APPROVED'

        dispatch.save()

        return redirect('dispatch_list')

    return render(
        request,
        'inventory/dispatch_detail.html',
        {
            'dispatch': dispatch
        }
    )