# Generated by Django 3.0.5 on 2020-05-01 18:56

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Disciplines', '0003_auto_20200501_1840'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='discipline',
            name='prepod_access',
        ),
    ]