from django.db import models
from django.contrib.auth.models import  AbstractUser
import uuid

# Create your models here.
class StudentUser(AbstractUser):
    phone_no=models.CharField(max_length=11,null=False,blank=False)
    location=models.CharField(max_length=100,blank=False)
    email=models.EmailField(unique=True,blank=False)

    def __str__(self):
        return self.username
class PasswordReset(models.Model):
    user=models.ForeignKey(StudentUser,on_delete=models.CASCADE)
    reset_id=models.UUIDField(default=uuid.uuid4,unique=True,editable=False)
    created_when = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Password reset for {self.user.username} at {self.created_when}"



