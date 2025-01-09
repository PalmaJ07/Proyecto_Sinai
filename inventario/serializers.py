import base64
from rest_framework import serializers
from .models import *
from usuarios.models import User

class ProductoSerializer(serializers.ModelSerializer):
    encrypted_id = serializers.SerializerMethodField()
    config_categoria = serializers.PrimaryKeyRelatedField(queryset=ConfigCategoria.objects.all())
    config_marca = serializers.PrimaryKeyRelatedField(queryset=ConfigMarca.objects.all())

    class Meta:
        model = Producto
        fields = ['encrypted_id', 'config_categoria', 'config_marca', 'descripcion', 'codigo',
                  'created_user', 'update_user', 'deleted_user', 'created_at', 'update_at', 'deleted_at']

    def get_encrypted_id(self, obj):
        return base64.urlsafe_b64encode(str(obj.id).encode()).decode()

class ProductoDetalleSerializer(serializers.ModelSerializer):
    encrypted_id = serializers.SerializerMethodField()
    producto = serializers.PrimaryKeyRelatedField(queryset=Producto.objects.all())
    config_unidad_medida = serializers.PrimaryKeyRelatedField(queryset=ConfigUnidadMedida.objects.all())
    config_presentacion_producto = serializers.PrimaryKeyRelatedField(queryset=ConfigPresentacionProducto.objects.all())
    almacen = serializers.PrimaryKeyRelatedField(queryset=ConfigAlmacen.objects.all())
    proveedor = serializers.PrimaryKeyRelatedField(queryset=ConfigProveedor.objects.all())

    class Meta:
        model = ProductoDetalle
        fields = ['encrypted_id', 'producto', 'config_unidad_medida', 'peso', 
                  'config_presentacion_producto', 'cantidad_por_presentacion', 
                  'unidades_por_presentacion', 'total_unidades', 'almacen', 
                  'precio_venta_presentacion', 'precio_venta_unidades', 'proveedor', 'fecha_expiracion',
                  'created_user', 'update_user', 'deleted_user', 'created_at', 'update_at', 'deleted_at']

    def get_encrypted_id(self, obj):
        return base64.urlsafe_b64encode(str(obj.id).encode()).decode()

class ProductoDetalleIngresoSerializer(serializers.ModelSerializer):
    encrypted_id = serializers.SerializerMethodField()
    producto = serializers.PrimaryKeyRelatedField(queryset=Producto.objects.all())
    producto_detalle = serializers.PrimaryKeyRelatedField(queryset=ProductoDetalle.objects.all())
    config_almacen = serializers.PrimaryKeyRelatedField(queryset=ConfigAlmacen.objects.all())
    producto_movimiento = serializers.PrimaryKeyRelatedField(queryset=ProductoMovimiento.objects.all(), required=False)
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())

    class Meta:
        model = ProductoDetalleIngreso
        fields = ['encrypted_id', 'producto', 'producto_detalle', 'config_almacen', 
                  'producto_movimiento', 'user', 'cantidad_por_presentacion', 
                  'unidades_por_presentacion', 'precio_compra_presentacion', 
                  'precio_compra_unidades', 'fecha_expiracion', 'fecha_ingreso', 
                  'created_user', 'update_user', 'deleted_user', 'created_at', 'update_at', 'deleted_at']

    def get_encrypted_id(self, obj):
        return base64.urlsafe_b64encode(str(obj.id).encode()).decode()

class ProductoDevolucionSerializer(serializers.ModelSerializer):
    encrypted_id = serializers.SerializerMethodField()
    producto_detalle = ProductoDetalleSerializer()

    class Meta:
        model = ProductoDevolucion
        fields = ['encrypted_id', 'producto_detalle', 'cantidad_por_presentacion', 
                  'unidades_por_presentacion', 'fecha', 'fecha_expiracion', 
                  'created_user', 'update_user', 'deleted_user', 'created_at', 'update_at', 'deleted_at']

    def get_encrypted_id(self, obj):
        return base64.urlsafe_b64encode(str(obj.id).encode()).decode()

class ProductoMovimientoSerializer(serializers.ModelSerializer):
    encrypted_id = serializers.SerializerMethodField()
    producto_detalle_origen = serializers.StringRelatedField()
    producto_detalle_destino = serializers.StringRelatedField()

    class Meta:
        model = ProductoMovimiento
        fields = ['encrypted_id', 'producto_detalle_origen', 'producto_detalle_destino', 
                  'cantidad_por_presentacion', 'unidades_por_presentacion', 'fecha', 
                  'fecha_expiracion', 'created_user', 'update_user', 'deleted_user', 
                  'created_at', 'update_at', 'deleted_at']

    def get_encrypted_id(self, obj):
        return base64.urlsafe_b64encode(str(obj.id).encode()).decode()
