import json
from django_cron import CronJobBase, Schedule


from channels.models import Channel
from channels.producers import producer, delivery_channel_report


class CronGetChannels(CronJobBase):
    RUN_EVERY_MINS = 3  # every 3 minute

    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = "channels.cron.CronGetChannels"  # a unique code

    def do(self):
        channels = Channel.objects.filter(isActive__in=[True]).all()
        for channel in channels:
            content = channel.to_dict()
            producer.produce(
                "youtube-watcher-channels-updates",
                key=str(content.pop("id")),
                value=json.dumps(content),
                on_delivery=delivery_channel_report,
            )
            producer.flush()
