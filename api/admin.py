from django.contrib import admin
from .models import UserDetail, Blog

# Register your models here.
class UserDetailAdmin(admin.ModelAdmin):
    # Define any customizations for the admin interface here
    pass
admin.site.register(UserDetail, UserDetailAdmin)

# Register your models here.
class BlogAdmin(admin.ModelAdmin):
    # Define any customizations for the admin interface here
    pass
admin.site.register(Blog, BlogAdmin)