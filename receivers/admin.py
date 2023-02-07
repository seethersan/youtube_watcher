from django.contrib import admin
from receivers.models import Receiver, Message


class ReceiverAdmin(admin.ModelAdmin):
    list_display = ("type", "get_profile", "channel", "isActive")

    @admin.display(description="Profile")
    def get_profile(self, obj):
        return obj.profile.username


class MessageAdmin(admin.ModelAdmin):
    list_display = ("get_receiver", "body", "sent", "error")

    @admin.display(description="Receiver")
    def get_receiver(self, obj):
        return (
            obj.receiver.type
            + " "
            + obj.receiver.channel
            + " - "
            + obj.profile.username
        )


admin.site.register(Receiver, ReceiverAdmin)
admin.site.register(Message, MessageAdmin)
