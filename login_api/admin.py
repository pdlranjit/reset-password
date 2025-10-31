from django.contrib import admin
from .models import StudentUser,PasswordReset

# Register your models here.
admin.site.register(StudentUser)
admin.site.register(PasswordReset)