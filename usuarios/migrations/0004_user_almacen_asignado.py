# Generated by Django 5.1.1 on 2025-01-22 01:48

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('configuraciones', '0003_alter_configalmacen_abreviatura_and_more'),
        ('usuarios', '0003_cliente'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='almacen_asignado',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='usuario_almacen', to='configuraciones.configalmacen'),
        ),
    ]
