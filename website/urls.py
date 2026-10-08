from django.urls import path

from . import views

app_name = "website"

urlpatterns = [
    path("", views.home, name="home"),
    path("about-us/", views.about, name="about"),
    path("our-services/", views.services, name="services"),
    path("contact/", views.contact, name="contact"),
]