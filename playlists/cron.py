import json
from django_cron import CronJobBase, Schedule


from playlists.models import Playlist
from playlists.producers import producer, delivery_playlist_report


class CronGetPlaylists(CronJobBase):
    RUN_EVERY_MINS = 3  # every 3 minute

    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = "playlists.cron.CronGetPlaylists"  # a unique code

    def do(self):
        playlists = Playlist.objects.filter(isActive__in=[True]).all()
        for playlist in playlists:
            content = playlist.to_dict()
            producer.produce(
                "youtube-watcher-playlists-updates",
                key=str(content.pop("id")),
                value=json.dumps(content),
                on_delivery=delivery_playlist_report,
            )
            producer.flush()
