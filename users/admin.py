from django.contrib import admin
from users.models import Profile


class ProfileAdmin(admin.ModelAdmin):
    list_display = ("username", "email", "google_api_key")


admin.site.register(Profile, ProfileAdmin)
