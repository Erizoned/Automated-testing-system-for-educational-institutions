# Generated by Django 5.0 on 2023-12-05 17:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Quiz', '0008_delete_testcopy'),
    ]

    operations = [
        migrations.AddField(
            model_name='test',
            name='is_completed',
            field=models.BooleanField(default=False),
        ),
    ]
