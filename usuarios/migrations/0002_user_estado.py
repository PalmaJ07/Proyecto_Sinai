# Generated by Django 5.1.1 on 2024-09-27 03:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('usuarios', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='estado',
            field=models.IntegerField(choices=[(1, 'Activo'), (0, 'Inactivo')], default=1),
        ),
    ]
