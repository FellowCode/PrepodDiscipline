# Generated by Django 3.0.5 on 2020-05-13 16:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Prepods', '0011_auto_20200513_1601'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='prepod',
            name='prosmotr',
        ),
        migrations.RemoveField(
            model_name='prepod',
            name='raspred',
        ),
        migrations.AddField(
            model_name='prepod',
            name='prava',
            field=models.CharField(choices=[('raspred', 'Распределение и просмотр'), ('prosmotr', 'Только просмотр по кафедре'), (None, 'НЕТ')], default=None, max_length=128, null=True, verbose_name='Права'),
        ),
    ]
