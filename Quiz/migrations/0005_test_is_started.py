# Generated by Django 4.2.7 on 2023-12-02 10:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Quiz', '0004_alter_test_time_limit'),
    ]

    operations = [
        migrations.AddField(
            model_name='test',
            name='is_started',
            field=models.BooleanField(default=False),
        ),
    ]
