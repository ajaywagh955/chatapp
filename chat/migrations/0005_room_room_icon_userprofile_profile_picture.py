# Generated by Django 5.0 on 2023-12-25 17:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0004_userprofile_friends'),
    ]

    operations = [
        migrations.AddField(
            model_name='room',
            name='room_icon',
            field=models.ImageField(blank=True, null=True, upload_to='room_icon/'),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='profile_picture',
            field=models.ImageField(blank=True, null=True, upload_to='profile_pics/'),
        ),
    ]
