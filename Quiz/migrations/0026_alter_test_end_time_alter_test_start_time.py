# Generated by Django 4.2.7 on 2023-12-20 08:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Quiz', '0025_test_is_published'),
    ]

    operations = [
        migrations.AlterField(
            model_name='test',
            name='end_time',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='test',
            name='start_time',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]