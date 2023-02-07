# Generated by Django 4.1.5 on 2023-02-03 05:02

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("channels", "0009_remove_video_dislikes"),
    ]

    operations = [
        migrations.AddConstraint(
            model_name="channel",
            constraint=models.UniqueConstraint(
                fields=("owner", "channel_id"), name="owner_channel_id"
            ),
        ),
    ]
