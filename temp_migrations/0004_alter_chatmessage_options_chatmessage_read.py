# Generated by Django 5.2 on 2025-04-21 18:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('listings', '0003_alter_listing_property_type_chatmessage'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='chatmessage',
            options={'ordering': ['created_at'], 'verbose_name': 'Chat Message', 'verbose_name_plural': 'Chat Messages'},
        ),
        migrations.AddField(
            model_name='chatmessage',
            name='read',
            field=models.BooleanField(default=False),
        ),
    ]
