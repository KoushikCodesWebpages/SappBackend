from django.db import models
from django.contrib.auth.models import User
from sapp.utils.base_model import BaseDBModel
# Create your models here.


class ProfileBase(BaseDBModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='profile_images/', null=True, blank=True)

    class Meta:
        abstract = True
        

class Standard(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name


class Section(models.Model):
    section_id = models.CharField(max_length=1, primary_key=True)
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name
    
class Subject(models.Model):
    
    subject_id = models.CharField(max_length=10, primary_key=True)
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

