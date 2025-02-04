import base64
from rest_framework import serializers
from .models import Venta, VentaDetalle
from usuarios.models import User,Cliente
from inventario.models import ProductoDetalle

class VentaDetalleSerializer(serializers.ModelSerializer):
    encrypted_id = serializers.SerializerMethodField()
    producto_detalle = serializers.PrimaryKeyRelatedField(queryset=ProductoDetalle.objects.all())
    venta = serializers.PrimaryKeyRelatedField(queryset=Venta.objects.all())

    class Meta:
        model = VentaDetalle
        fields = [
            'encrypted_id', 'id', 'producto_detalle', 'venta', 'descuento', 'cantidad', 
            'unidades', 'descuento_porcentual', 'precio_venta', 
            'created_user', 'updated_user', 'deleted_user', 
            'created_at', 'updated_at', 'deleted_at'
        ]

    def get_encrypted_id(self, obj):
        if isinstance(obj, dict):
            return None  # Retornar None si aún no hay ID
        return base64.urlsafe_b64encode(str(obj.id).encode()).decode()


class VentaSerializer(serializers.ModelSerializer):
    encrypted_id = serializers.SerializerMethodField()
    cliente = serializers.PrimaryKeyRelatedField(queryset=Cliente.objects.all(), required=False)
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    empleado_nombre = serializers.CharField(source='user.name', read_only=True)

    print(empleado_nombre)
    
    class Meta:
        model = Venta
        fields = [
            'encrypted_id', 'id', 'cliente', 'user','empleado_nombre', 'cliente_nombre', 
            'total_sin_descuento', 'descuento', 'descuento_porcentual', 
            'total_venta', 'fecha_venta', 'comentario', 'comentario_devolucion', 
            'devolucion', 'anulacion', 
            'created_user', 'updated_user', 'deleted_user', 
            'created_at', 'updated_at', 'deleted_at'
        ]

    def get_encrypted_id(self, obj):
        return base64.urlsafe_b64encode(str(obj.id).encode()).decode()
