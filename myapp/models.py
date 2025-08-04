from django.db import models

# Create your models here.
class Users(models.Model):
    Account = models.CharField(max_length=15)
    UserName = models.CharField(max_length=40, blank=False, null=False)
    Password = models.CharField(max_length=12, blank=False, null=False, default='0000')
    Email = models.CharField(max_length=40, blank=False, null=False)
    AuthCode = models.CharField(max_length=40, blank=False, null=False)
    AuthPass = models.BooleanField(default=False)

    class Meta:
        db_table = "Users"


class OffStreetCP(models.Model):
    id = models.AutoField(primary_key=True)
    car_park_id = models.CharField(max_length=20)
    city = models.CharField(max_length=50)
    name = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)
    faredescription = models.TextField(null=True, blank=True)
    address = models.CharField(max_length=200, null=True, blank=True)
    emergency_phone = models.CharField(max_length=50, null=True, blank=True)
    position_lat = models.FloatField(null=True, blank=True)
    position_lon = models.FloatField(null=True, blank=True)

    class Meta:
        unique_together = ("car_park_id", "city")

    def __str__(self):
        return f"{self.name} ({self.city} - {self.car_park_id})"


class OffStreetPSA(models.Model):
    id = models.AutoField(primary_key=True)
    car_park_id = models.CharField(max_length=20)
    city = models.CharField(max_length=50)
    total_spaces = models.IntegerField(null=True, blank=True)
    available_spaces = models.IntegerField(null=True, blank=True)

    class Meta:
        unique_together = ("car_park_id", "city")

    def __str__(self):
        return f"{self.city} - {self.car_park_id}：可用 {self.available_spaces} / {self.total_spaces}"


class DBUpdateTime(models.Model):
    id = models.AutoField(primary_key=True)  # 主鍵
    db = models.CharField(max_length=50)  # 資料表名稱
    city = models.CharField(max_length=50)  # 城市
    updatetime = models.DateTimeField(null=True, blank=True)  # 更新時間

    class Meta:
        unique_together = ("db", "city")  # 確保 db 和 city 組合唯一

    def __str__(self):
        return f"{self.db} - {self.city} ({self.updatetime})"
