from django.db import models


class CompanyInfo(models.Model):
    company_name = models.CharField(
        max_length=200,
        default="Panchamul"
    )

    tagline = models.CharField(
        max_length=255,
        blank=True
    )

    about_title = models.CharField(
        max_length=255,
        default="About Us"
    )

    about_description = models.TextField(
        blank=True
    )

    phone = models.CharField(
        max_length=50,
        blank=True
    )

    email = models.EmailField(
        blank=True
    )

    address = models.TextField(
        blank=True
    )

    facebook_url = models.URLField(
        blank=True
    )

    instagram_url = models.URLField(
        blank=True
    )

    youtube_url = models.URLField(
        blank=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
        return self.company_name


class WebsiteProduct(models.Model):

    name = models.CharField(
        max_length=200
    )

    description = models.TextField(
        blank=True
    )

    image = models.ImageField(
        upload_to="website/products/",
        blank=True,
        null=True
    )

    is_active = models.BooleanField(
        default=True
    )

    display_order = models.PositiveIntegerField(
        default=0
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return self.name


class WebsiteGallery(models.Model):

    title = models.CharField(
        max_length=200,
        blank=True
    )

    image = models.ImageField(
        upload_to="website/gallery/"
    )

    description = models.TextField(
        blank=True
    )

    is_active = models.BooleanField(
        default=True
    )

    display_order = models.PositiveIntegerField(
        default=0
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return self.title or f"Gallery {self.id}"


class ContactInquiry(models.Model):

    name = models.CharField(
        max_length=200
    )

    phone = models.CharField(
        max_length=50
    )

    email = models.EmailField(
        blank=True
    )

    subject = models.CharField(
        max_length=255,
        blank=True
    )

    message = models.TextField()

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    is_read = models.BooleanField(
        default=False
    )

    def __str__(self):
        return f"{self.name} - {self.phone}"



    