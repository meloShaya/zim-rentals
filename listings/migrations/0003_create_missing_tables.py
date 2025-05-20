# Generated manually

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('listings', '0002_add_is_direct_message_field'),
    ]

    operations = [
        migrations.CreateModel(
            name='ChatMessage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('message', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('is_read', models.BooleanField(default=False)),
                ('read_at', models.DateTimeField(blank=True, null=True)),
                ('listing', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='chat_messages', to='listings.listing')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='chat_messages', to='accounts.customuser')),
            ],
            options={
                'verbose_name': 'Chat Message',
                'verbose_name_plural': 'Chat Messages',
                'ordering': ['created_at'],
            },
        ),
        migrations.CreateModel(
            name='RoommateProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(help_text='Brief title for your roommate search', max_length=100)),
                ('age', models.PositiveIntegerField(help_text='Your age')),
                ('gender', models.CharField(choices=[('M', 'Male'), ('F', 'Female'), ('O', 'Other'), ('N', 'Prefer not to say')], max_length=1)),
                ('city', models.CharField(max_length=50)),
                ('suburb', models.CharField(blank=True, max_length=50)),
                ('min_budget', models.DecimalField(decimal_places=2, help_text='Your minimum budget', max_digits=10)),
                ('max_budget', models.DecimalField(decimal_places=2, help_text='Your maximum budget', max_digits=10)),
                ('move_in_date', models.DateField(help_text='When are you looking to move in?')),
                ('lifestyle', models.CharField(blank=True, choices=[('early_bird', 'Early Bird'), ('night_owl', 'Night Owl'), ('social', 'Social/Outgoing'), ('quiet', 'Quiet/Private'), ('studious', 'Studious'), ('neat', 'Neat and Tidy'), ('relaxed', 'Relaxed about cleaning')], max_length=20)),
                ('bio', models.TextField(help_text='Tell potential roommates about yourself')),
                ('preferences', models.TextField(blank=True, help_text="Describe what you're looking for in a roommate or housing")),
                ('is_smoker', models.BooleanField(default=False)),
                ('has_pets', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('is_active', models.BooleanField(default=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='roommate_profile', to='accounts.customuser')),
            ],
        ),
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
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='saved_searches', to='accounts.customuser')),
            ],
            options={
                'verbose_name': 'Saved Search',
                'verbose_name_plural': 'Saved Searches',
            },
        ),
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