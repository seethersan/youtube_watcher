from djongo import models
from users.models import Profile
from encrypted_model_fields.fields import EncryptedCharField

RECEIVER_TYPES = (
    ("email", "Email"),
    ("slack", "Slack"),
    ("discord", "Discord"),
    ("telegram", "Telegram"),
)


class Receiver(models.Model):
    type = models.CharField(max_length=100, choices=RECEIVER_TYPES)
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    token = EncryptedCharField(max_length=100, blank=True, null=True)
    channel = models.CharField(max_length=100)
    isActive = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.type} {self.channel} - {self.profile.username}"


class Message(models.Model):
    receiver = models.ForeignKey(Receiver, on_delete=models.CASCADE)
    body = models.TextField()
    sent = models.BooleanField(default=True)
    error = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.receiver}: {self.body} "
