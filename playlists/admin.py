from django.contrib import admin
from playlists.models import Playlist, Video


class PlaylistAdmin(admin.ModelAdmin):
    list_display = ("name", "playlist_id", "description", "isActive")


class VideoAdmin(admin.ModelAdmin):
    list_display = ("title", "video_id", "description", "isActive")


admin.site.register(Playlist, PlaylistAdmin)
admin.site.register(Video, VideoAdmin)
