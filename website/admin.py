from django.contrib import admin

from .models import (
    CompanyInfo,
    WebsiteProduct,
    WebsiteGallery,
    ContactInquiry,
)


@admin.register(CompanyInfo)
class CompanyInfoAdmin(admin.ModelAdmin):

    list_display = (
        "company_name",
        "phone",
        "email",
        "updated_at",
    )


@admin.register(WebsiteProduct)
class WebsiteProductAdmin(admin.ModelAdmin):

    list_display = (
        "name",
        "is_active",
        "display_order",
        "created_at",
    )

    list_filter = (
        "is_active",
    )

    ordering = (
        "display_order",
        "-id",
    )


@admin.register(WebsiteGallery)
class WebsiteGalleryAdmin(admin.ModelAdmin):

    list_display = (
        "title",
        "is_active",
        "display_order",
        "created_at",
    )

    list_filter = (
        "is_active",
    )

    ordering = (
        "display_order",
        "-id",
    )


@admin.register(ContactInquiry)
class ContactInquiryAdmin(admin.ModelAdmin):

    list_display = (
        "name",
        "phone",
        "email",
        "subject",
        "is_read",
        "created_at",
    )

    list_filter = (
        "is_read",
        "created_at",
    )

    search_fields = (
        "name",
        "phone",
        "email",
        "subject",
        "message",
    )

    ordering = (
        "-created_at",
    )