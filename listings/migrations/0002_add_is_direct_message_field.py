# Generated manually

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('listings', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='listing',
            name='is_direct_message',
            field=models.BooleanField(default=False, help_text='Flag for listings created for direct messaging only'),
        ),
        migrations.AddField(
            model_name='listing',
            name='featured_image',
            field=models.ImageField(blank=True, null=True, upload_to='listings/'),
        ),
        migrations.AddField(
            model_name='listing',
            name='phone_number',
            field=models.CharField(default='000-000-0000', help_text='Contact phone number', max_length=20),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='listing',
            name='whatsapp_number',
            field=models.CharField(blank=True, help_text='WhatsApp number (optional)', max_length=20),
        ),
    ] 