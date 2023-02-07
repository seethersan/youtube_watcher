from djongo import models


from users.models import Profile


class Channel(models.Model):
    name = models.CharField(max_length=100)
    channel_id = models.CharField(max_length=100)
    description = models.TextField()
    subscribers = models.IntegerField(blank=True, default=0)
    views = models.IntegerField(blank=True, default=0)
    likes = models.IntegerField(blank=True, default=0)
    comments = models.IntegerField(blank=True, default=0)
    isActive = models.BooleanField(default=True)
    owner = models.ForeignKey(
        Profile, on_delete=models.CASCADE, related_name="profile_channels"
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["owner", "channel_id"], name="owner_channel_id"
            )
        ]

    def __str__(self):
        return self.name

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "channel_id": self.channel_id,
            "description": self.description,
            "subscribers": self.subscribers,
            "views": self.views,
            "likes": self.likes,
            "comments": self.comments,
            "isActive": self.isActive,
            "owner": self.owner_id,
        }


class Video(models.Model):
    title = models.CharField(max_length=100)
    video_id = models.CharField(max_length=100)
    description = models.TextField()
    views = models.IntegerField(blank=True, default=0)
    likes = models.IntegerField(blank=True, default=0)
    comments = models.IntegerField(blank=True, default=0)
    isActive = models.BooleanField(default=True)
    thumbnail = models.CharField(max_length=250, blank=True)
    channel = models.ForeignKey(
        Channel, on_delete=models.CASCADE, related_name="channel_videos"
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["video_id", "channel_id"], name="video_id_channel_id"
            )
        ]

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "video_id": self.video_id,
            "description": self.description,
            "views": self.views,
            "likes": self.likes,
            "comments": self.comments,
            "isActive": self.isActive,
            "thumbnail": self.thumbnail,
            "channel": self.channel_id,
        }

    def __str__(self):
        return self.title
