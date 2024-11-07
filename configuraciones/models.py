from django.db import models
from django.utils import timezone

# Create your models here.
class ConfigCategoria(models.Model):
    nombre = models.CharField(max_length=255, unique=True)
    abreviatura = models.CharField(max_length=50, unique=True)
    orden = models.IntegerField()

    # Columnas adicionales
    created_user = models.ForeignKey('usuarios.User', on_delete=models.SET_NULL, related_name='created_categorias', null=True, blank=True)
    update_user = models.ForeignKey('usuarios.User', on_delete=models.SET_NULL, related_name='updated_categorias', null=True, blank=True)
    deleted_user = models.ForeignKey('usuarios.User', on_delete=models.SET_NULL, related_name='deleted_categorias', null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = "Categoría"
        verbose_name_plural = "Categorías"
        ordering = ['orden']


# Aplicar lo mismo para otros modelos:

class ConfigMarca(models.Model):
    nombre = models.CharField(max_length=255, unique=True)
    abreviatura = models.CharField(max_length=50, unique=True)
    orden = models.IntegerField()

    # Columnas adicionales
    created_user = models.ForeignKey('usuarios.User', on_delete=models.SET_NULL, related_name='created_marcas', null=True, blank=True)
    update_user = models.ForeignKey('usuarios.User', on_delete=models.SET_NULL, related_name='updated_marcas', null=True, blank=True)
    deleted_user = models.ForeignKey('usuarios.User', on_delete=models.SET_NULL, related_name='deleted_marcas', null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = "Marca"
        verbose_name_plural = "Marcas"
        ordering = ['orden']

# Similar para los demás modelos (Almacen, PresentacionProducto, UnidadMedida, Proveedor):

class ConfigAlmacen(models.Model):
    nombre = models.CharField(max_length=255, unique=True)
    abreviatura = models.CharField(max_length=50, unique=True)
    orden = models.IntegerField()

    # Columnas adicionales
    created_user = models.ForeignKey('usuarios.User', on_delete=models.SET_NULL, related_name='created_almacenes', null=True, blank=True)
    update_user = models.ForeignKey('usuarios.User', on_delete=models.SET_NULL, related_name='updated_almacenes', null=True, blank=True)
    deleted_user = models.ForeignKey('usuarios.User', on_delete=models.SET_NULL, related_name='deleted_almacenes', null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = "Almacén"
        verbose_name_plural = "Almacenes"
        ordering = ['orden']

# ConfigPresentacionProducto:

class ConfigPresentacionProducto(models.Model):
    nombre = models.CharField(max_length=255, unique=True)
    abreviatura = models.CharField(max_length=50, unique=True)
    orden = models.IntegerField()

    # Columnas adicionales
    created_user = models.ForeignKey('usuarios.User', on_delete=models.SET_NULL, related_name='created_presentaciones', null=True, blank=True)
    update_user = models.ForeignKey('usuarios.User', on_delete=models.SET_NULL, related_name='updated_presentaciones', null=True, blank=True)
    deleted_user = models.ForeignKey('usuarios.User', on_delete=models.SET_NULL, related_name='deleted_presentaciones', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = "Presentación de Producto"
        verbose_name_plural = "Presentaciones de Productos"
        ordering = ['orden']


class ConfigUnidadMedida(models.Model):
    nombre = models.CharField(max_length=255, unique=True)
    abreviatura = models.CharField(max_length=50, unique=True)
    orden = models.IntegerField()

    # Columnas adicionales
    created_user = models.ForeignKey('usuarios.User', on_delete=models.SET_NULL, related_name='created_unidad_medida', null=True, blank=True)
    update_user = models.ForeignKey('usuarios.User', on_delete=models.SET_NULL, related_name='updated_unidad_medida', null=True, blank=True)
    deleted_user = models.ForeignKey('usuarios.User', on_delete=models.SET_NULL, related_name='deleted_unidad_medida', null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = "Unidad de Medida"
        verbose_name_plural = "Unidades de Medida"
        ordering = ['orden']


# Modelo para la tabla con atributos específicos de proveedor
class ConfigProveedor(models.Model):
    nombre_proveedor = models.CharField(max_length=255, unique=True)
    telefono = models.CharField(max_length=50)
    encargado = models.CharField(max_length=50)
    telefono_encargado = models.CharField(max_length=50)

    # Columnas adicionales
    created_user = models.ForeignKey('usuarios.User', on_delete=models.SET_NULL, related_name='created_proveedor', null=True, blank=True)
    update_user = models.ForeignKey('usuarios.User', on_delete=models.SET_NULL, related_name='updated_proveedor', null=True, blank=True)
    deleted_user = models.ForeignKey('usuarios.User', on_delete=models.SET_NULL, related_name='deleted_proveedor', null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.nombre_proveedor

    class Meta:
        verbose_name = "Proveedor"
        verbose_name_plural = "Proveedores"