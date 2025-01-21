import base64
from rest_framework import serializers
from .models import User, Cliente

class UserSerializer(serializers.ModelSerializer):

    encrypted_id = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['encrypted_id', 'name', 'id_personal', 'phone', 'username', 'password', 'user_type', 'estado',
                  'created_user', 'update_user', 'deleted_user']
        extra_kwargs = {
            'password': {'write_only': True}
       }
    
    # Método para encriptar el ID usando Base64
    def get_encrypted_id(self, obj):
        # Codificar el id en Base64
        return base64.urlsafe_b64encode(str(obj.id).encode()).decode()

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        instance = self.Meta.model(**validated_data)
        if password is not None:
            instance.set_password(password)
        instance.save()
        return instance

# Serializer para Cliente
class ClienteSerializer(serializers.ModelSerializer):
    encrypted_id = serializers.SerializerMethodField()

    class Meta:
        model = Cliente
        fields = ['encrypted_id','id', 'nombre', 'telefono', 'direccion', 'id_personal',
                   'created_user', 'update_user', 'deleted_user']
        
    # Método para encriptar el ID usando Base64
    def get_encrypted_id(self, obj):
        # Codificar el id en Base64
        return base64.urlsafe_b64encode(str(obj.id).encode()).decode()