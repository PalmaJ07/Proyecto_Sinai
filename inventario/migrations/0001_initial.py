# Generated by Django 5.1.1 on 2025-01-08 02:28

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('configuraciones', '0003_alter_configalmacen_abreviatura_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Producto',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('descripcion', models.CharField(max_length=255)),
                ('codigo', models.CharField(max_length=255)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('update_at', models.DateTimeField(auto_now=True)),
                ('deleted_at', models.DateTimeField(blank=True, null=True)),
                ('config_categoria', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='productos', to='configuraciones.configcategoria')),
                ('config_marca', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='productos', to='configuraciones.configmarca')),
                ('created_user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='created_productos', to=settings.AUTH_USER_MODEL)),
                ('deleted_user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='deleted_productos', to=settings.AUTH_USER_MODEL)),
                ('update_user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='updated_productos', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Producto',
                'verbose_name_plural': 'Productos',
                'ordering': ['descripcion'],
            },
        ),
        migrations.CreateModel(
            name='ProductoDetalle',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('peso', models.FloatField()),
                ('cantidad_por_presentacion', models.IntegerField()),
                ('unidades_por_presentacion', models.IntegerField()),
                ('total_unidades', models.IntegerField()),
                ('precio_venta_presentacion', models.DecimalField(decimal_places=2, max_digits=10)),
                ('precio_venta_unidades', models.DecimalField(decimal_places=2, max_digits=10)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('update_at', models.DateTimeField(auto_now=True)),
                ('deleted_at', models.DateTimeField(blank=True, null=True)),
                ('almacen', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='producto_detalles', to='configuraciones.configalmacen')),
                ('config_presentacion_producto', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='producto_detalles', to='configuraciones.configpresentacionproducto')),
                ('config_unidad_medida', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='producto_detalles', to='configuraciones.configunidadmedida')),
                ('created_user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='created_producto_detalles', to=settings.AUTH_USER_MODEL)),
                ('deleted_user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='deleted_producto_detalles', to=settings.AUTH_USER_MODEL)),
                ('producto', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='detalles', to='inventario.producto')),
                ('proveedor', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='producto_detalles', to='configuraciones.configproveedor')),
                ('update_user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='updated_producto_detalles', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Producto Detalle',
                'verbose_name_plural': 'Productos Detalles',
                'ordering': ['producto', 'config_presentacion_producto'],
            },
        ),
        migrations.CreateModel(
            name='ProductoDevolucion',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('cantidad_por_presentacion', models.IntegerField()),
                ('unidades_por_presentacion', models.IntegerField()),
                ('fecha', models.DateField()),
                ('fecha_expiracion', models.DateField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('update_at', models.DateTimeField(auto_now=True)),
                ('deleted_at', models.DateTimeField(blank=True, null=True)),
                ('created_user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='created_producto_devoluciones', to=settings.AUTH_USER_MODEL)),
                ('deleted_user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='deleted_producto_devoluciones', to=settings.AUTH_USER_MODEL)),
                ('producto_detalle', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='devoluciones', to='inventario.productodetalle')),
                ('update_user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='updated_producto_devoluciones', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Producto Devolución',
                'verbose_name_plural': 'Productos Devoluciones',
                'ordering': ['fecha', 'producto_detalle'],
            },
        ),
        migrations.CreateModel(
            name='ProductoMovimiento',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('cantidad_por_presentacion', models.IntegerField()),
                ('unidades_por_presentacion', models.IntegerField()),
                ('fecha', models.DateField()),
                ('fecha_expiracion', models.DateField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('update_at', models.DateTimeField(auto_now=True)),
                ('deleted_at', models.DateTimeField(blank=True, null=True)),
                ('created_user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='created_producto_movimientos', to=settings.AUTH_USER_MODEL)),
                ('deleted_user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='deleted_producto_movimientos', to=settings.AUTH_USER_MODEL)),
                ('producto_detalle_destino', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='movimientos_destino', to='configuraciones.configalmacen')),
                ('producto_detalle_origen', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='movimientos_origen', to='configuraciones.configalmacen')),
                ('update_user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='updated_producto_movimientos', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Producto Movimiento',
                'verbose_name_plural': 'Productos Movimientos',
                'ordering': ['fecha', 'producto_detalle_origen'],
            },
        ),
        migrations.CreateModel(
            name='ProductoDetalleIngreso',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('cantidad_por_presentacion', models.IntegerField()),
                ('unidades_por_presentacion', models.IntegerField()),
                ('precio_compra_presentacion', models.DecimalField(decimal_places=2, max_digits=10)),
                ('precio_compra_unidades', models.DecimalField(decimal_places=2, max_digits=10)),
                ('fecha_expiracion', models.DateField(blank=True, null=True)),
                ('fecha_ingreso', models.DateField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('update_at', models.DateTimeField(auto_now=True)),
                ('deleted_at', models.DateTimeField(blank=True, null=True)),
                ('config_almacen', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='ingresos', to='configuraciones.configalmacen')),
                ('created_user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='created_producto_ingresos', to=settings.AUTH_USER_MODEL)),
                ('deleted_user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='deleted_producto_ingresos', to=settings.AUTH_USER_MODEL)),
                ('producto', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ingresos', to='inventario.producto')),
                ('producto_detalle', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ingresos', to='inventario.productodetalle')),
                ('update_user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='updated_producto_ingresos', to=settings.AUTH_USER_MODEL)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='ingresos_producto_detalle', to=settings.AUTH_USER_MODEL)),
                ('producto_movimiento', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='ingresos', to='inventario.productomovimiento')),
            ],
            options={
                'verbose_name': 'Producto Detalle Ingreso',
                'verbose_name_plural': 'Productos Detalles Ingresos',
                'ordering': ['fecha_ingreso', 'producto_detalle'],
            },
        ),
    ]
