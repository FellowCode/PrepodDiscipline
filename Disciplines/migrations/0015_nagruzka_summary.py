# Generated by Django 3.0.5 on 2020-05-17 21:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Disciplines', '0014_auto_20200517_1554'),
    ]

    operations = [
        migrations.AddField(
            model_name='nagruzka',
            name='summary',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=5),
        ),
    ]