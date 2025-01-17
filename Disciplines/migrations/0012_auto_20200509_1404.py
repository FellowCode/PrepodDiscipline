# Generated by Django 3.0.5 on 2020-05-09 14:04

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('Disciplines', '0011_auto_20200508_1918'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='archive',
            options={'verbose_name': 'Архив', 'verbose_name_plural': 'Архивы'},
        ),
        migrations.AlterModelOptions(
            name='discipline',
            options={'ordering': ['name'], 'verbose_name': 'Дисциплина', 'verbose_name_plural': 'Дисциплины'},
        ),
        migrations.AlterField(
            model_name='archive',
            name='dt',
            field=models.DateTimeField(auto_now_add=True, verbose_name='Дата'),
        ),
        migrations.AlterField(
            model_name='nagruzka',
            name='archive',
            field=models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='nagruzki', to='Disciplines.Archive'),
        ),
    ]
