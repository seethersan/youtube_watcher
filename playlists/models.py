from djongo import models


from users.models import Profile


class Playlist(models.Model):
    name = models.CharField(max_length=100)
    playlist_id = models.CharField(max_length=100)
    description = models.TextField()
    subscribers = models.IntegerField(blank=True, default=0)
    views = models.IntegerField(blank=True, default=0)
    likes = models.IntegerField(blank=True, default=0)
    comments = models.IntegerField(blank=True, default=0)
    isActive = models.BooleanField(default=True)
    owner = models.ForeignKey(
        Profile, on_delete=models.CASCADE, related_name="profile_playlists"
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["owner", "playlist_id"], name="owner_playlist_id"
            )
        ]

    def __str__(self):
        return self.name

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "playlist_id": self.playlist_id,
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
    playlist = models.ForeignKey(
        Playlist, on_delete=models.CASCADE, related_name="playlist_videos"
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["video_id", "playlist_id"], name="video_id_playlist_id"
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
            "playlist": self.playlist_id,
        }

    def __str__(self):
        return self.title
