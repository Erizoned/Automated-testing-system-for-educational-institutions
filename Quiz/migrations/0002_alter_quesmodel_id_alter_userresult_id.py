# Generated by Django 4.2.7 on 2023-12-01 19:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Quiz', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='quesmodel',
            name='id',
            field=models.AutoField(primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='userresult',
            name='id',
            field=models.AutoField(primary_key=True, serialize=False),
        ),
    ]
