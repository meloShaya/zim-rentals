# Generated by Django 5.2 on 2025-04-22 19:04

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('listings', '0007_listing_is_direct_message'),
    ]

    operations = [
        migrations.CreateModel(
            name='SocialShare',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('source', models.CharField(choices=[('whatsapp', 'WhatsApp'), ('facebook', 'Facebook'), ('twitter', 'Twitter/X'), ('email', 'Email'), ('other', 'Other')], max_length=20)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('clicks', models.PositiveIntegerField(default=1)),
                ('ip_address', models.GenericIPAddressField(blank=True, null=True)),
                ('listing', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='social_shares', to='listings.listing')),
            ],
            options={
                'verbose_name': 'Social Share',
                'verbose_name_plural': 'Social Shares',
                'unique_together': {('listing', 'source', 'ip_address')},
            },
        ),
    ]
