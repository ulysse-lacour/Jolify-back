# from django.contrib import admin
# from django.contrib.auth.admin import UserAdmin
# from apps.models import User

# admin.site.register(User, UserAdmin)

from django.contrib import admin
from apps.models import User


@admin.register(User)
class UniversalAdmin(admin.ModelAdmin):
    def get_list_display(self, request):
        return [field.name for field in self.model._meta.concrete_fields]
