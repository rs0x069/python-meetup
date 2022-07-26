# Generated by Django 4.0.6 on 2022-07-27 20:38

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('meetups', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='question',
            name='answer',
            field=models.TextField(blank=True, db_index=True, verbose_name='Ответ'),
        ),
        migrations.AlterField(
            model_name='question',
            name='section',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='questions', to='meetups.section', verbose_name='Блок мероприятия'),
        ),
        migrations.AlterField(
            model_name='question',
            name='visitor',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='questions', to='meetups.visitor', verbose_name='Посетитель'),
        ),
        migrations.AlterField(
            model_name='section',
            name='event',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sections', to='meetups.event', verbose_name='Мероприятие'),
        ),
        migrations.AlterField(
            model_name='speaker',
            name='section',
            field=models.ManyToManyField(related_name='speakers', to='meetups.section', verbose_name='Блок мероприятия'),
        ),
        migrations.AlterField(
            model_name='speaker',
            name='telegram_id',
            field=models.CharField(max_length=16, unique=True, verbose_name='Telegram ID'),
        ),
        migrations.AlterField(
            model_name='visitor',
            name='about_oneself',
            field=models.TextField(blank=True, verbose_name='О себе'),
        ),
        migrations.AlterField(
            model_name='visitor',
            name='phone_number',
            field=models.CharField(blank=True, db_index=True, max_length=16, verbose_name='Телефон'),
        ),
        migrations.AlterField(
            model_name='visitor',
            name='telegram_id',
            field=models.CharField(max_length=16, unique=True, verbose_name='Telegram ID'),
        ),
    ]
