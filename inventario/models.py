from django.db import models
from configuraciones.models import ConfigCategoria, ConfigMarca, ConfigUnidadMedida, ConfigPresentacionProducto, ConfigAlmacen, ConfigProveedor

class Producto(models.Model):
    id = models.BigAutoField(primary_key=True)
    config_categoria = models.ForeignKey(ConfigCategoria, on_delete=models.PROTECT, related_name='productos')
    config_marca = models.ForeignKey(ConfigMarca, on_delete=models.PROTECT, related_name='productos')
    descripcion = models.CharField(max_length=255)
    codigo = models.CharField(max_length=255)

    # Columnas adicionales
    created_user = models.ForeignKey('usuarios.User', on_delete=models.SET_NULL, related_name='created_productos', null=True, blank=True)
    update_user = models.ForeignKey('usuarios.User', on_delete=models.SET_NULL, related_name='updated_productos', null=True, blank=True)
    deleted_user = models.ForeignKey('usuarios.User', on_delete=models.SET_NULL, related_name='deleted_productos', null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.descripcion} ({self.codigo})"

    class Meta:
        verbose_name = "Producto"
        verbose_name_plural = "Productos"
        ordering = ['descripcion']

class ProductoDetalle(models.Model):
    id = models.BigAutoField(primary_key=True)
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name='detalles')
    config_unidad_medida = models.ForeignKey(ConfigUnidadMedida, on_delete=models.PROTECT, related_name='producto_detalles')
    peso = models.FloatField()
    config_presentacion_producto = models.ForeignKey(ConfigPresentacionProducto, on_delete=models.PROTECT, related_name='producto_detalles')
    cantidad_por_presentacion = models.IntegerField(null=True, blank=True)
    unidades_por_presentacion = models.IntegerField(null=True, blank=True)
    total_unidades = models.IntegerField(null=True, blank=True)
    almacen = models.ForeignKey(ConfigAlmacen, on_delete=models.PROTECT, related_name='producto_detalles', null=True, blank=True)
    precio_venta_presentacion = models.DecimalField(max_digits=10, decimal_places=2)
    precio_venta_unidades = models.DecimalField(max_digits=10, decimal_places=2)
    proveedor = models.ForeignKey(ConfigProveedor, on_delete=models.PROTECT, related_name='producto_detalles')
    fecha_expiracion = models.DateField(null=True, blank=True)

    # Columnas adicionales
    created_user = models.ForeignKey('usuarios.User', on_delete=models.SET_NULL, related_name='created_producto_detalles', null=True, blank=True)
    update_user = models.ForeignKey('usuarios.User', on_delete=models.SET_NULL, related_name='updated_producto_detalles', null=True, blank=True)
    deleted_user = models.ForeignKey('usuarios.User', on_delete=models.SET_NULL, related_name='deleted_producto_detalles', null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Detalle de {self.producto} - {self.config_presentacion_producto}"

    class Meta:
        verbose_name = "Producto Detalle"                          
        verbose_name_plural = "Productos Detalles"
        ordering = ['producto', 'config_presentacion_producto']

class ProductoMovimiento(models.Model):
    id = models.BigAutoField(primary_key=True)
    producto_detalle_origen = models.ForeignKey(ConfigAlmacen, on_delete=models.CASCADE, related_name='movimientos_origen')
    producto_detalle_destino = models.ForeignKey(ConfigAlmacen, on_delete=models.CASCADE, related_name='movimientos_destino')
    cantidad_por_presentacion = models.IntegerField()
    unidades_por_presentacion = models.IntegerField()
    fecha = models.DateField()
    fecha_expiracion = models.DateField(null=True, blank=True)

    # Columnas adicionales
    created_user = models.ForeignKey('usuarios.User', on_delete=models.SET_NULL, related_name='created_producto_movimientos', null=True, blank=True)
    update_user = models.ForeignKey('usuarios.User', on_delete=models.SET_NULL, related_name='updated_producto_movimientos', null=True, blank=True)
    deleted_user = models.ForeignKey('usuarios.User', on_delete=models.SET_NULL, related_name='deleted_producto_movimientos', null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Movimiento de {self.producto_detalle_origen} a {self.producto_detalle_destino}"

    class Meta:
        verbose_name = "Producto Movimiento"
        verbose_name_plural = "Productos Movimientos"
        ordering = ['fecha', 'producto_detalle_origen']
        
class ProductoDetalleIngreso(models.Model):
    id = models.BigAutoField(primary_key=True)
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name='ingresos')
    producto_detalle = models.ForeignKey(ProductoDetalle, on_delete=models.CASCADE, related_name='ingresos')
    config_almacen = models.ForeignKey(ConfigAlmacen, on_delete=models.PROTECT, related_name='ingresos')
    producto_movimiento = models.ForeignKey(ProductoMovimiento, on_delete=models.SET_NULL, related_name='ingresos', null=True, blank=True)
    user = models.ForeignKey('usuarios.User', on_delete=models.PROTECT, related_name='ingresos_producto_detalle')
    cantidad_por_presentacion = models.IntegerField()
    unidades_por_presentacion = models.IntegerField()
    precio_compra_presentacion = models.DecimalField(max_digits=10, decimal_places=2)
    precio_compra_unidades = models.DecimalField(max_digits=10, decimal_places=2)
    fecha_expiracion = models.DateField(null=True, blank=True)
    fecha_ingreso = models.DateField()

    # Columnas adicionales
    created_user = models.ForeignKey('usuarios.User', on_delete=models.SET_NULL, related_name='created_producto_ingresos', null=True, blank=True)
    update_user = models.ForeignKey('usuarios.User', on_delete=models.SET_NULL, related_name='updated_producto_ingresos', null=True, blank=True)
    deleted_user = models.ForeignKey('usuarios.User', on_delete=models.SET_NULL, related_name='deleted_producto_ingresos', null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Ingreso de {self.producto_detalle} en {self.config_almacen} - {self.fecha_ingreso}"

    class Meta:
        verbose_name = "Producto Detalle Ingreso"
        verbose_name_plural = "Productos Detalles Ingresos"
        ordering = ['fecha_ingreso', 'producto_detalle']

class ProductoDevolucion(models.Model):
    id = models.BigAutoField(primary_key=True)
    producto_detalle = models.ForeignKey(ProductoDetalle, on_delete=models.CASCADE, related_name='devoluciones')
    cantidad_por_presentacion = models.IntegerField()
    unidades_por_presentacion = models.IntegerField()
    fecha = models.DateField()
    fecha_expiracion = models.DateField(null=True, blank=True)

    # Columnas adicionales
    created_user = models.ForeignKey('usuarios.User', on_delete=models.SET_NULL, related_name='created_producto_devoluciones', null=True, blank=True)
    update_user = models.ForeignKey('usuarios.User', on_delete=models.SET_NULL, related_name='updated_producto_devoluciones', null=True, blank=True)
    deleted_user = models.ForeignKey('usuarios.User', on_delete=models.SET_NULL, related_name='deleted_producto_devoluciones', null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Devolución de {self.producto_detalle} - {self.fecha}"

    class Meta:
        verbose_name = "Producto Devolución"
        verbose_name_plural = "Productos Devoluciones"
        ordering = ['fecha', 'producto_detalle']

