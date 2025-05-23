# Generated by Django 5.2 on 2025-04-22 20:32

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('listings', '0008_socialshare'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='SavedSearch',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='Name this search for your reference', max_length=100)),
                ('city', models.CharField(blank=True, choices=[('harare', 'Harare'), ('bulawayo', 'Bulawayo'), ('mutare', 'Mutare'), ('gweru', 'Gweru'), ('masvingo', 'Masvingo'), ('chitungwiza', 'Chitungwiza')], max_length=20, null=True)),
                ('suburb', models.CharField(blank=True, max_length=100, null=True)),
                ('property_type', models.CharField(blank=True, choices=[('single', 'Single Room'), ('shared', 'Shared Room'), ('cottage', 'Cottage'), ('apartment', 'Apartment'), ('house', 'House')], max_length=100, null=True)),
                ('max_price', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('min_price', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('bedrooms', models.PositiveIntegerField(blank=True, null=True)),
                ('bathrooms', models.PositiveIntegerField(blank=True, null=True)),
                ('is_furnished', models.BooleanField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('last_sent_at', models.DateTimeField(blank=True, help_text='When the last alert was sent', null=True)),
                ('is_active', models.BooleanField(default=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='saved_searches', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Saved Search',
                'verbose_name_plural': 'Saved Searches',
            },
        ),
    ]
