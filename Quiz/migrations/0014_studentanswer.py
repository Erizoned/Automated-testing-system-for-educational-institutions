# Generated by Django 4.2.7 on 2023-12-11 17:40

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('Quiz', '0013_quesmodel_question_type_quesmodel_user_answer'),
    ]

    operations = [
        migrations.CreateModel(
            name='StudentAnswer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('answer_text', models.TextField(blank=True, null=True)),
                ('selected_option', models.CharField(blank=True, max_length=200, null=True)),
                ('question', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Quiz.quesmodel')),
                ('user_result', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Quiz.userresult')),
            ],
        ),
    ]