# Generated by Django 3.0.5 on 2020-05-01 18:40

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Prepods', '0003_auto_20200501_1720'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='prepod',
            name='disciplines',
        ),
    ]