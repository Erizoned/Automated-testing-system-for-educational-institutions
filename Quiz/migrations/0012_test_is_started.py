# Generated by Django 4.2.7 on 2023-12-09 08:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Quiz', '0011_alter_test_end_time_alter_test_start_time'),
    ]

    operations = [
        migrations.AddField(
            model_name='test',
            name='is_started',
            field=models.BooleanField(default=False),
        ),
    ]