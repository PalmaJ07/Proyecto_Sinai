import base64
from rest_framework import serializers
from .models import *

# Serializer categoria
class ConfigCategoriaSerializer(serializers.ModelSerializer):
    encrypted_id = serializers.SerializerMethodField()

    class Meta:
        model = ConfigCategoria
        fields = ['encrypted_id', 'nombre', 'abreviatura', 'orden', 
                  'created_user', 'update_user', 'deleted_user', 
                  'created_at', 'update_at', 'deleted_at']

    def get_encrypted_id(self, obj):
        return base64.urlsafe_b64encode(str(obj.id).encode()).decode()

# Serializer marca
class ConfigMarcaSerializer(serializers.ModelSerializer):
    encrypted_id = serializers.SerializerMethodField()

    class Meta:
        model = ConfigMarca
        fields = ['encrypted_id', 'nombre', 'abreviatura', 'orden', 
                  'created_user', 'update_user', 'deleted_user', 
                  'created_at', 'update_at', 'deleted_at']

    def get_encrypted_id(self, obj):
        return base64.urlsafe_b64encode(str(obj.id).encode()).decode()

# Serializer almacen
class ConfigAlmacenSerializer(serializers.ModelSerializer):
    encrypted_id = serializers.SerializerMethodField()

    class Meta:
        model = ConfigAlmacen
        fields = ['encrypted_id', 'nombre', 'abreviatura', 'orden', 
                  'created_user', 'update_user', 'deleted_user', 
                  'created_at', 'update_at', 'deleted_at']

    def get_encrypted_id(self, obj):
        return base64.urlsafe_b64encode(str(obj.id).encode()).decode()

# Serializer presentaciones
class ConfigPresentacionProductoSerializer(serializers.ModelSerializer):
    encrypted_id = serializers.SerializerMethodField()

    class Meta:
        model = ConfigPresentacionProducto
        fields = ['encrypted_id', 'nombre', 'abreviatura', 'orden', 
                  'created_user', 'update_user', 'deleted_user', 
                  'created_at', 'update_at', 'deleted_at']

    def get_encrypted_id(self, obj):
        return base64.urlsafe_b64encode(str(obj.id).encode()).decode()

# Serializer unidad de medida 
class ConfigUnidadMedidaSerializer(serializers.ModelSerializer):
    encrypted_id = serializers.SerializerMethodField()

    class Meta:
        model = ConfigUnidadMedida
        fields = ['encrypted_id', 'nombre', 'abreviatura', 'orden', 
                  'created_user', 'update_user', 'deleted_user', 
                  'created_at', 'update_at', 'deleted_at']

    def get_encrypted_id(self, obj):
        return base64.urlsafe_b64encode(str(obj.id).encode()).decode()

# Serializer proveedor
class ConfigProveedorSerializer(serializers.ModelSerializer):
    encrypted_id = serializers.SerializerMethodField()

    class Meta:
        model = ConfigProveedor
        fields = ['encrypted_id', 'nombre_proveedor', 'telefono', 'encargado', 'telefono_encargado', 
                  'created_user', 'update_user', 'deleted_user', 
                  'created_at', 'update_at', 'deleted_at']

    def get_encrypted_id(self, obj):
        return base64.urlsafe_b64encode(str(obj.id).encode()).decode()