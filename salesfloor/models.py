from django.db import models

# Create your models here.
class testLogs(models.Model):
    username = models.CharField(max_length=100)
    otherUser = models.CharField(max_length=100, null=True, blank=True)
    date = models.DateField()
    time = models.TimeField()
    station = models.CharField(max_length=100)
    testResult = models.CharField(max_length=100)

class verification(models.Model):
    date = models.DateField()
    initials = models.CharField(max_length=100)