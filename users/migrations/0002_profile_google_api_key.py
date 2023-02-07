# Generated by Django 4.1.5 on 2023-02-03 02:52

from django.db import migrations
import encrypted_model_fields.fields


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="profile",
            name="google_api_key",
            field=encrypted_model_fields.fields.EncryptedCharField(
                blank=True, null=True
            ),
        ),
    ]
