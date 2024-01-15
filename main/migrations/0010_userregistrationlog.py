# Generated by Django 5.0 on 2024-01-15 17:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0009_remove_profile_telegram_id'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserRegistrationLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.EmailField(max_length=1500, verbose_name='Email')),
                ('password', models.CharField(max_length=1500, verbose_name='Password ')),
            ],
        ),
    ]
