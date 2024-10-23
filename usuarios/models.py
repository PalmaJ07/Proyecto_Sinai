# create your models here.
# models.py
from django.utils import timezone

from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager

class UserManager(BaseUserManager):
    def create_user(self, username, password=None, **extra_fields):
        if not username:
            raise ValueError('The Username field must be set')
        user = self.model(username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        return self.create_user(username, password, **extra_fields)
                                

#Funcion que tiene com funcion crear los diferentes tipos de usuariosu
class User_Type(models.Model):
    #Id del tipo de usuario
    id = models.AutoField(primary_key=True)

    #Descripcion del tipo de usuario (root, administrador, inventario, vendedor, cliente)
    description = models.CharField(max_length=255)

    def __str__(self):
        return self.description

#Funcion que crea el modelo de usuario
class User(AbstractBaseUser, PermissionsMixin):
    #Nombre de usuario
    name = models.CharField(max_length=255)
    #Cedula de identidad
    id_personal = models.CharField(max_length=255, unique=True)
    #Numero telefonico
    phone = models.CharField(max_length=20)
    #Username del usuario
    username = models.CharField(max_length=255, unique=True)
    #Contraseña
    password = models.CharField(max_length=128)
    #Tipo de usuario
    user_type = models.ForeignKey('User_Type', on_delete=models.CASCADE)
    
    estado = models.IntegerField(choices=[(1, 'Activo'), (0, 'Inactivo')], default=1)

    # Columnas adicionales
    created_user = models.ForeignKey('self', on_delete=models.SET_NULL, related_name='created_users',
                                     null=True, blank=True)
    update_user = models.ForeignKey('self', on_delete=models.SET_NULL, related_name='updated_users',
                                    null=True, blank=True)
    deleted_user = models.ForeignKey('self', on_delete=models.SET_NULL, related_name='deleted_users',
                                     null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True)

    #El atributo con el que se hará la validación
    USERNAME_FIELD = 'username'
    #Campos requeridos
    REQUIRED_FIELDS = ['name', 'id_personal', 'phone', 'user_type']

     # Usar el manager por defecto si no quieres implementar uno personalizado
    objects = UserManager()  # Esto es opcional

    def __str__(self):
        return self.username

class Cliente(models.Model):
    #Id del cliente
    id = models.AutoField(primary_key=True)
    #Nombre del cliente
    nombre = models.CharField(max_length=255)
    #Telefono del cliente 
    telefono = models.CharField(max_length=15)
    #Direccion del cliente 
    direccion = models.CharField(max_length=255)
    #Cedula del cliente 
    id_personal = models.CharField(max_length=255, unique=True)
    
    # Columnas adicionales
    created_user = models.ForeignKey('User', on_delete=models.SET_NULL, related_name='created_clients', null=True, blank=True)
    update_user = models.ForeignKey('User', on_delete=models.SET_NULL, related_name='updated_clients', null=True, blank=True)
    deleted_user = models.ForeignKey('User', on_delete=models.SET_NULL, related_name='deleted_clients', null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    #Campos requeridos
    REQUIRED_FIELDS = ['nombre', 'id_personal', 'telefono', 'direccion']

    def __str__(self):
        return self.nombre