# Generated by Django 4.1.5 on 2023-02-01 05:08

from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="playlists",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=100)),
                ("playlist_id", models.CharField(max_length=100)),
                ("description", models.TextField()),
                ("subscribers", models.IntegerField()),
                ("views", models.IntegerField()),
                ("likes", models.IntegerField()),
                ("comments", models.IntegerField()),
                ("videos", models.IntegerField()),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("is_active", models.BooleanField(default=True)),
            ],
        ),
    ]
