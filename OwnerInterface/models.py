from django.db import models
from django.contrib.auth.models import User
# Create your models here.



class ParkingLot(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)  # 業主
    image = models.ImageField(upload_to='parking_images/', null=True, blank=True)
    name = models.CharField(max_length=100)
    floor = models.CharField(max_length=10)
    total_slots = models.IntegerField()
    available_slots = models.IntegerField()
    location = models.CharField(max_length=255)

    def __str__(self):
        return self.name


