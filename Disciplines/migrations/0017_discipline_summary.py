# Generated by Django 3.0.5 on 2020-05-20 19:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Disciplines', '0016_auto_20200520_1925'),
    ]

    operations = [
        migrations.AddField(
            model_name='discipline',
            name='summary',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10, verbose_name='ИТОГО'),
        ),
    ]
