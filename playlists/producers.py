import json
from django.dispatch import receiver
from django.db.models.signals import pre_save
from confluent_kafka import SerializingProducer


from playlists.models import Playlist, Video
from youtube_watcher.settings import KAFKA_BOOTSTRAP_SERVERS


def delivery_playlist_report(err, msg):
    if err is not None:
        print("Delivery failed for Playlist record {}: {}".format(msg.key(), err))
        return
    print(
        "Playlist record {} successfully produced to {} [{}] at offset {}".format(
            msg.key(), msg.topic(), msg.partition(), msg.offset()
        )
    )


def delivery_playlist_changes_report(err, msg):
    if err is not None:
        print(
            "Delivery failed for Playlist CHanges record {}: {}".format(msg.key(), err)
        )
        return
    print(
        "Playlist Changes record {} successfully produced to {} [{}] at offset {}".format(
            msg.key(), msg.topic(), msg.partition(), msg.offset()
        )
    )


def delivery_video_report(err, msg):
    if err is not None:
        print("Delivery failed for Video record {}: {}".format(msg.key(), err))
        return
    print(
        "Video record {} successfully produced to {} [{}] at offset {}".format(
            msg.key(), msg.topic(), msg.partition(), msg.offset()
        )
    )


def delivery_video_changes_report(err, msg):
    if err is not None:
        print("Delivery failed for Video Changes record {}: {}".format(msg.key(), err))
        return
    print(
        "Video Changes record {} successfully produced to {} [{}] at offset {}".format(
            msg.key(), msg.topic(), msg.partition(), msg.offset()
        )
    )


producer_config = {
    "bootstrap.servers": KAFKA_BOOTSTRAP_SERVERS,
}

producer = SerializingProducer(producer_config)


@receiver(pre_save, sender=Playlist)
def playlist_changed(sender, instance, **kwargs):
    try:
        obj = sender.objects.get(id=instance.id)
    except sender.DoesNotExist:
        pass
    else:
        changes = []
        for field in sender._meta.fields:
            if getattr(obj, field.name) != getattr(instance, field.name):
                changes.append(
                    f"{field.name}: {getattr(obj, field.name)} -> {getattr(instance, field.name)}"
                )
        if changes:
            producer.produce(
                "youtube-watcher-playlists-changes",
                key=str(instance.id),
                value="\n".join(changes),
                on_delivery=delivery_playlist_changes_report,
            )


@receiver(pre_save, sender=Video)
def video_changed(sender, instance, **kwargs):
    try:
        obj = sender.objects.get(id=instance.id)
    except sender.DoesNotExist:
        pass
    else:
        changes = []
        for field in sender._meta.fields:
            if getattr(obj, field.name) != getattr(instance, field.name):
                changes.append(
                    f"{field.name}: {getattr(obj, field.name)} -> {getattr(instance, field.name)}"
                )
        if changes:
            video = {
                "owner": instance.playlist.owner.id,
                "message": instance.title + "\n" + "\n".join(changes),
            }
            producer.produce(
                "youtube-watcher-videos-changes",
                key=str(instance.id),
                value=json.dumps(video),
                on_delivery=delivery_video_changes_report,
            )
