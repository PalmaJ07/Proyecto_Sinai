from rest_framework import serializers
from .models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'name', 'id_personal', 'phone', 'username', 'password', 'user_type', 'estado',
                  'created_user', 'update_user', 'deleted_user']
        extra_kwargs = {
            'password': {'write_only': True}
       }

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        instance = self.Meta.model(**validated_data)
        if password is not None:
            instance.set_password(password)
        instance.save()
        return instance
