# Generated by Django 3.0.5 on 2020-05-02 13:06

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Disciplines', '0005_discipline_prepod_available'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='discipline',
            name='prepod_available',
        ),
    ]