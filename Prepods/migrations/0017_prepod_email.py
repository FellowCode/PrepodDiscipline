# Generated by Django 3.0.5 on 2020-05-29 21:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Prepods', '0016_auto_20200527_2319'),
    ]

    operations = [
        migrations.AddField(
            model_name='prepod',
            name='email',
            field=models.EmailField(max_length=254, null=True, verbose_name='Email'),
        ),
    ]
