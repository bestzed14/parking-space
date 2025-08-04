from django.db import models
from django.contrib.auth.models import User
# Create your models here.
class LicensePlate(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    plate_number = models.CharField(max_length=20)

    def __str__(self):
        return self.plate_number

class CreditCard(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    card_number = models.CharField(max_length=20)

    def __str__(self):
        return f"{self.user.username}'s card"