# Generated by Django 4.2.7 on 2023-12-16 10:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Quiz', '0019_customuser_group'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='subjects',
            field=models.ManyToManyField(blank=True, related_name='users', to='Quiz.subject'),
        ),
    ]
