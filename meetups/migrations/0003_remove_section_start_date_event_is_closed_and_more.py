# Generated by Django 4.0.6 on 2022-07-30 11:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('meetups', '0002_alter_question_answer_alter_question_section_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='section',
            name='start_date',
        ),
        migrations.AddField(
            model_name='event',
            name='is_closed',
            field=models.BooleanField(default=0, verbose_name='Закрыто'),
        ),
        migrations.AddField(
            model_name='section',
            name='speaker',
            field=models.ManyToManyField(related_name='section_speakers', to='meetups.visitor', verbose_name='Спикер'),
        ),
        migrations.AddField(
            model_name='visitor',
            name='is_speaker',
            field=models.BooleanField(default=0, verbose_name='Спикер'),
        ),
        migrations.AlterField(
            model_name='visitor',
            name='company',
            field=models.CharField(blank=True, db_index=True, max_length=64, verbose_name='Компания'),
        ),
        migrations.AlterField(
            model_name='visitor',
            name='email',
            field=models.EmailField(blank=True, db_index=True, max_length=32, verbose_name='Email'),
        ),
        migrations.AlterField(
            model_name='visitor',
            name='position',
            field=models.CharField(blank=True, db_index=True, max_length=64, verbose_name='Должность'),
        ),
        migrations.DeleteModel(
            name='Speaker',
        ),
    ]
