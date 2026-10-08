from django.contrib import messages
from django.shortcuts import redirect, render

from .models import (
    CompanyInfo,
    WebsiteProduct,
    WebsiteGallery,
    ContactInquiry,
)


# -------------------------------------------------
# HOME
# -------------------------------------------------

def home(request):

    company = CompanyInfo.objects.first()

    products = WebsiteProduct.objects.filter(
        is_active=True
    ).order_by(
        "display_order",
        "-id"
    )

    gallery = WebsiteGallery.objects.filter(
        is_active=True
    ).order_by(
        "display_order",
        "-id"
    )

    context = {
        "company": company,
        "products": products,
        "gallery": gallery,
    }

    return render(request, "home.html", context)


# -------------------------------------------------
# ABOUT US
# -------------------------------------------------

def about(request):

    company = CompanyInfo.objects.first()

    context = {
        "company": company,
    }

    return render(request, "aboutus.html", context)


# -------------------------------------------------
# OUR SERVICES
# -------------------------------------------------

def services(request):

    company = CompanyInfo.objects.first()

    products = WebsiteProduct.objects.filter(
        is_active=True
    ).order_by(
        "display_order",
        "-id"
    )

    gallery = WebsiteGallery.objects.filter(
        is_active=True
    ).order_by(
        "display_order",
        "-id"
    )

    context = {
        "company": company,
        "products": products,
        "gallery": gallery,
    }

    return render(request, "services.html", context)


# -------------------------------------------------
# CONTACT
# -------------------------------------------------

def contact(request):

    company = CompanyInfo.objects.first()

    context = {
        "company": company,
    }

    if request.method == "POST":

        full_name = request.POST.get("full_name", "").strip()
        email = request.POST.get("email", "").strip()
        phone = request.POST.get("phone", "").strip()
        message = request.POST.get("message", "").strip()

        # ---------------- VALIDATION ----------------
        # On error the page is re-rendered (not redirected),
        # so the visitor's typed values stay in the form.

        error = None

        if not full_name:
            error = "Please enter your full name."
        elif not email:
            error = "Please enter your email."
        elif not phone:
            error = "Please enter your phone number."
        elif not message:
            error = "Please enter your message."

        if error:
            messages.error(request, error)
            return render(request, "contact.html", context)

        # ---------------- SAVE ----------------

        ContactInquiry.objects.create(
            full_name=full_name,
            email=email,
            phone=phone,
            message=message,
        )

        messages.success(
            request,
            "Thank you! Your message has been sent successfully."
        )

        return redirect("website:contact")

    return render(request, "contact.html", context)