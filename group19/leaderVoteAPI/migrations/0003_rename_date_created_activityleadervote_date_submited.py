# Generated by Django 4.2.13 on 2024-05-13 21:48

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('leaderVoteAPI', '0002_activityleadervote_date_created'),
    ]

    operations = [
        migrations.RenameField(
            model_name='activityleadervote',
            old_name='date_created',
            new_name='date_submited',
        ),
    ]
