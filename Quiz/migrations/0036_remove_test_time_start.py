# Generated by Django 4.2.7 on 2023-12-25 09:58

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Quiz', '0035_userresult_is_completed'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='test',
            name='time_start',
        ),
    ]
