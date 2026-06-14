from django.db import models
from django.conf import settings



class Dealer(models.Model):

    name = models.CharField(max_length=200)

    address = models.TextField()

    phone = models.CharField(max_length=20)

    email = models.EmailField(
        blank=True,
        null=True
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='dealers'
    )
    is_active = models.BooleanField(
        default=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return self.name
    

class DealerProfile(models.Model):

    dealer = models.OneToOneField(
        Dealer,
        on_delete=models.CASCADE
    )

    admin_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'DEALER_ADMIN'}
    )

    def __str__(self):
        return self.dealer.name
    




