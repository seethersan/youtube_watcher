# Generated by Django 4.1.5 on 2023-02-03 04:23

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("playlists", "0005_rename_is_active_playlist_isactive_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="playlist",
            name="comments",
            field=models.IntegerField(null=True),
        ),
        migrations.AlterField(
            model_name="playlist",
            name="likes",
            field=models.IntegerField(null=True),
        ),
        migrations.AlterField(
            model_name="playlist",
            name="subscribers",
            field=models.IntegerField(null=True),
        ),
        migrations.AlterField(
            model_name="playlist",
            name="views",
            field=models.IntegerField(null=True),
        ),
        migrations.AlterField(
            model_name="video",
            name="comments",
            field=models.IntegerField(null=True),
        ),
        migrations.AlterField(
            model_name="video",
            name="dislikes",
            field=models.IntegerField(null=True),
        ),
        migrations.AlterField(
            model_name="video",
            name="likes",
            field=models.IntegerField(null=True),
        ),
        migrations.AlterField(
            model_name="video",
            name="views",
            field=models.IntegerField(null=True),
        ),
    ]
