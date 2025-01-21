from django.db import models
from usuarios.models import User

class Venta(models.Model):
    cliente = models.ForeignKey('usuarios.Cliente', on_delete=models.SET_NULL, null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    cliente_nombre = models.CharField(max_length=255, null=True, blank=True)
    total_sin_descuento = models.FloatField()
    descuento = models.FloatField(null=True, blank=True)
    descuento_porcentual = models.BooleanField(default=True)
    total_venta = models.FloatField()
    fecha_venta = models.DateField()
    comentario = models.CharField(max_length=255, null=True, blank=True)
    comentario_devolucion = models.CharField(max_length=255, null=True, blank=True)
    devolucion = models.BooleanField(default=False)
    anulacion = models.BooleanField(default=False)

    created_user = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='created_ventas', null=True, blank=True)
    updated_user = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='updated_ventas', null=True, blank=True)
    deleted_user = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='deleted_ventas', null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Venta #{self.id} - Total: {self.total_venta}"


class VentaDetalle(models.Model):
    producto_detalle = models.ForeignKey('inventario.ProductoDetalle', on_delete=models.CASCADE)
    venta = models.ForeignKey(Venta, on_delete=models.CASCADE, related_name='detalles')
    descuento = models.FloatField(null=True, blank=True)
    cantidad = models.IntegerField()
    unidades = models.BooleanField(default=True)
    descuento_porcentual = models.BooleanField(default=True)
    precio_venta = models.FloatField()

    created_user = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='created_detalles', null=True, blank=True)
    updated_user = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='updated_detalles', null=True, blank=True)
    deleted_user = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='deleted_detalles', null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Detalle #{self.id} - Venta #{self.venta.id}"