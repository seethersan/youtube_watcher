from django.contrib import admin
from channels.models import Channel, Video


class ChannelAdmin(admin.ModelAdmin):
    list_display = ("name", "channel_id", "description", "isActive")


class VideoAdmin(admin.ModelAdmin):
    list_display = ("title", "video_id", "description", "isActive")


admin.site.register(Channel, ChannelAdmin)
admin.site.register(Video, VideoAdmin)
