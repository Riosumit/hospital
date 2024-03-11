from django.contrib import admin
from .models import UserDetail

# Register your models here.
class UserDetailAdmin(admin.ModelAdmin):
    # Define any customizations for the admin interface here
    pass
admin.site.register(UserDetail, UserDetailAdmin)