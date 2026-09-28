from django.shortcuts import render, redirect, get_object_or_404
from .models import RawMaterial,Supplier
from .forms import MaterialIssueForm, RawMaterialForm,SupplierForm, ProductForm,ProductionForm
from django.contrib.auth.decorators import login_required
from django.db import transaction
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
    MaterialReturn,
    MaterialReturnItem,
    
   
)
from decimal import Decimal, InvalidOperation
from django.db.models import F

from .forms import (
    RawMaterialPurchaseForm,DispatchForm, MaterialReturnForm
)
from django.http import JsonResponse
import json
from decimal import Decimal
from inventory.models import DealerStock
from dealers.models import DealerLedger


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

            items_json = request.POST.get("items_json", "[]")

            items = json.loads(items_json)

            for item in items:

                material = RawMaterial.objects.get(
                    id=item['material']
                )

                qty_text = str(item.get("quantity", "")).strip()
                rate_text = str(item.get("rate", "")).strip()

                if qty_text == "" or rate_text == "":
                    continue

                try:

                    qty = Decimal(qty_text)

                    rate = Decimal(rate_text)

                except InvalidOperation:

                    continue

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

@login_required
def issue_create(request):

    form = MaterialIssueForm(
        request.POST or None
    )

    materials = RawMaterial.objects.filter(
        is_active=True
    )

    if request.method == "POST":

        if form.is_valid():

            items_json = request.POST.get(
                "items_json",
                "[]"
            )

            if not items_json:

                return render(
                    request,
                    "inventory/issue_create.html",
                    {
                        "form": form,
                        "materials": materials,
                        "error":
                            "Please add at least one material."
                    }
                )

            try:

                items = json.loads(
                    items_json
                )

            except json.JSONDecodeError:

                return render(
                    request,
                    "inventory/issue_create.html",
                    {
                        "form": form,
                        "materials": materials,
                        "error":
                            "Invalid material data."
                    }
                )

            if not items:

                return render(
                    request,
                    "inventory/issue_create.html",
                    {
                        "form": form,
                        "materials": materials,
                        "error":
                            "Please add at least one material."
                    }
                )

            # ==================================================
            # SAVE EVERYTHING AS ONE TRANSACTION
            # ==================================================

            try:

                with transaction.atomic():

                    # ------------------------------------------
                    # CREATE ISSUE
                    # ------------------------------------------

                    issue = form.save(
                        commit=False
                    )

                    issue.created_by = request.user

                    issue.save()

                    # ------------------------------------------
                    # PROCESS MATERIALS
                    # ------------------------------------------

                    for item in items:

                        material_id = item.get(
                            "material"
                        )

                        quantity_text = item.get(
                            "quantity"
                        )

                        if not material_id:

                            raise ValueError(
                                "Invalid material selected."
                            )

                        try:

                            qty = Decimal(
                                quantity_text
                            )

                        except (
                            InvalidOperation,
                            TypeError
                        ):

                            raise ValueError(
                                "Invalid quantity."
                            )

                        if qty <= 0:

                            raise ValueError(
                                "Quantity must be greater than zero."
                            )

                        # --------------------------------------
                        # GET MATERIAL
                        # --------------------------------------

                        material = RawMaterial.objects.get(
                            id=material_id,
                            is_active=True
                        )

                        # --------------------------------------
                        # STOCK CHECK
                        # --------------------------------------

                        if material.current_stock < qty:

                            raise ValueError(
                                f"Not enough stock for "
                                f"{material.name}. "
                                f"Available: "
                                f"{material.current_stock}, "
                                f"Requested: {qty}"
                            )

                        # --------------------------------------
                        # CREATE ISSUE ITEM
                        #
                        # IMPORTANT:
                        # This must NOT deduct stock itself.
                        # --------------------------------------

                        MaterialIssueItem.objects.create(
                            issue=issue,
                            raw_material=material,
                            quantity=qty
                        )

                        # --------------------------------------
                        # DEDUCT STOCK
                        #
                        # THIS IS THE ONLY PLACE WHERE
                        # STOCK IS DEDUCTED.
                        # --------------------------------------

                        material.current_stock -= qty

                        material.save(
                            update_fields=[
                                "current_stock"
                            ]
                        )

                # ==============================================
                # SUCCESS
                # ==============================================

                return redirect(
                    "issue_list"
                )

            except ValueError as e:

                return render(
                    request,
                    "inventory/issue_create.html",
                    {
                        "form": form,
                        "materials": materials,
                        "error": str(e)
                    }
                )

    return render(
        request,
        "inventory/issue_create.html",
        {
            "form": form,
            "materials": materials
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

    returns = MaterialReturn.objects.all().order_by("-id")

    return render(

        request,

        "inventory/return_list.html",

        {

            "returns": returns,

        }

    )




def return_create(request):

    form = MaterialReturnForm(
        request.POST or None
    )

    materials = RawMaterial.objects.filter(
        is_active=True
    )

    if request.method == "POST":

        if form.is_valid():

            material_return = form.save(
                commit=False
            )

            material_return.created_by = request.user

            material_return.save()

            items = json.loads(

                request.POST.get(
                    "items_json",
                    "[]"
                )

            )

            for item in items:

                qty = Decimal(

                    str(
                        item.get(
                            "quantity"
                        ) or "0"
                    )

                )

                if qty <= 0:
                    continue

                material = RawMaterial.objects.get(

                    id=item["material"]

                )

                MaterialReturnItem.objects.create(

                    material_return=material_return,

                    raw_material=material,

                    quantity=qty

                )

            return redirect(
                "return_list"
            )

    return render(

        request,

        "inventory/return_create.html",

        {

            "form": form,

            "materials": materials,

        }

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
                    str(
                        item.get(
                            "quantity_produced"
                        ) or "0"
                    )
                )

                qty_wasted = Decimal(
                    str(
                        item.get(
                            "quantity_wasted"
                        ) or "0"
                    )
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

            items_json = request.POST.get(
                'items_json'
            )

            if not items_json:

                return render(
                    request,
                    'inventory/dispatch_create.html',
                    {
                        'form': form,
                        'products': products,
                        'error': 'Please add at least one product.'
                    }
                )

            items = json.loads(
                items_json
            )

            dispatch = form.save(
                commit=False
            )

            dispatch.created_by = request.user

            dispatch.save()

            total_amount = Decimal('0')

            for item in items:

                product = Product.objects.get(
                    id=item['product']
                )

                qty = Decimal(
                    str(item['quantity'])
                )

                rate = Decimal(
                    str(item['rate'])
                )

                amount = Decimal(
                    str(item['amount'])
                )

                # Stock validation

                if product.current_stock < qty:

                    dispatch.delete()

                    return render(
                        request,
                        'inventory/dispatch_create.html',
                        {
                            'form': form,
                            'products': products,
                            'error':
                                f'Not enough stock for '
                                f'{product.name}. '
                                f'Available stock: '
                                f'{product.current_stock}'
                        }
                    )

                DispatchItem.objects.create(
                    dispatch=dispatch,
                    product=product,
                    dispatched_qty=qty,
                    rate=rate,
                    amount=amount
                )

                total_amount += amount

                # Deduct company stock

                product.current_stock -= qty

                product.save()

            dispatch.total_amount = total_amount

            dispatch.save()

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


# @login_required
# def dispatch_approval(request, pk):

#     dispatch = get_object_or_404(
#         Dispatch,
#         pk=pk
#     )

#     if request.method == 'POST':

#         # Prevent double approval

#         if dispatch.status == 'APPROVED':

#             return redirect(
#                 'dispatch_list'
#             )

#         for item in dispatch.items.all():

#             received_qty = Decimal(
#                 request.POST.get(
#                     f'received_{item.id}',
#                     0
#                 )
#             )

#             damaged_qty = Decimal(
#                 request.POST.get(
#                     f'damaged_{item.id}',
#                     0
#                 )
#             )

#             returned_qty = Decimal(
#                 request.POST.get(
#                     f'returned_{item.id}',
#                     0
#                 )
#             )

#             item.received_qty = received_qty
#             item.damaged_qty = damaged_qty
#             item.returned_qty = returned_qty

#             item.save()

#             # Update Dealer Stock

#             dealer_stock, created = (
#                 DealerStock.objects.get_or_create(
#                     dealer=dispatch.dealer,
#                     product=item.product,
#                     defaults={
#                         'quantity': Decimal('0')
#                     }
#                 )
#             )

#             dealer_stock.quantity += received_qty

#             dealer_stock.save()

#         # Create Dealer Ledger Entry

#         last_balance = DealerLedger.objects.filter(
#             dealer=dispatch.dealer
#         ).order_by(
#             '-id'
#         ).first()

#         balance = (
#             last_balance.balance
#             if last_balance
#             else Decimal('0')
#         )

#         balance += dispatch.total_amount

#         DealerLedger.objects.create(
#             dealer=dispatch.dealer,
#             entry_type='DISPATCH',
#             debit=dispatch.total_amount,
#             credit=Decimal('0'),
#             balance=balance,
#             reference=dispatch.dispatch_no
#         )

#         dispatch.status = 'APPROVED'

#         dispatch.save()

#         return redirect(
#             'dispatch_list'
#         )

#     return render(
#         request,
#         'inventory/dispatch_approval.html',
#         {
#             'dispatch': dispatch
#         }
#     )

