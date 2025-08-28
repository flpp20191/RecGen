from django.db import models
from audit.models import *
from django.contrib.auth.models import User

class UserInformation(models.Model):
    user_information = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=200, null=True, blank=True)
    address = models.CharField(max_length=200, null=True, blank=True)
    contact_number = models.CharField(max_length=20, null=True, blank=True)
    contact_email = models.CharField(max_length=200, null=True, blank=True)

    def __str__(self):
        return self.name if self.name else str(self.user_information)