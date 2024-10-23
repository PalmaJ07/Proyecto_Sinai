from django.shortcuts import render
import base64
from django.db.models import Q
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import *
from rest_framework import status
from rest_framework.exceptions import NotFound,AuthenticationFailed
from rest_framework.pagination import PageNumberPagination
from .models import *
from usuarios.models import  User
import jwt, datetime
from django.utils import timezone
    
# Create your views here.


################CATEGORIAS###########################
class RegisterCategoria(APIView):
    def post(self, request):
        # Extraer el token JWT de la cookie
        token = request.COOKIES.get('jwt')
        if not token:
            raise AuthenticationFailed('Unauthenticated!')

        try:
            payload = jwt.decode(token, 'secret', algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Unauthenticated!')
        except jwt.DecodeError:
            raise AuthenticationFailed('Invalid token!')

        # Obtener el usuario que está realizando la solicitud
        current_user = User.objects.filter(id=payload['id']).first()
        if not current_user:
            raise AuthenticationFailed('User not found!')

        # Crear un diccionario con los datos enviados en la solicitud
        data = request.data.copy()
        data['created_user'] = current_user.id
        data['update_user'] = None
        data['deleted_user'] = None

        # Serializar y validar los datos
        serializer = ConfigCategoriaSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)

class UpdateCategoria(APIView):
    def patch(self, request, encrypted_id):
        # Autenticación
        token = request.COOKIES.get('jwt')
        if not token:
            raise AuthenticationFailed('Unauthenticated!')

        try:
            payload = jwt.decode(token, 'secret', algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Unauthenticated!')
        except jwt.DecodeError:
            raise AuthenticationFailed('Invalid token!')

        # Decodificar el `encrypted_id` para obtener el ID real
        try:
            categoria_id = base64.urlsafe_b64decode(encrypted_id).decode()
        except Exception:
            return Response({'error': 'Invalid encrypted ID.'}, status=status.HTTP_400_BAD_REQUEST)

        # Buscar la categoría por ID
        try:
            categoria = ConfigCategoria.objects.get(id=categoria_id)
        except ConfigCategoria.DoesNotExist:
            return Response({'error': 'Category not found.'}, status=status.HTTP_404_NOT_FOUND)

        # Actualizar los campos que fueron enviados en el request
        serializer = ConfigCategoriaSerializer(categoria, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response({'message': 'Category updated successfully.'}, status=status.HTTP_200_OK)

class IndexCategoriaView(APIView):
    def get(self, request):
        # Autenticación mediante JWT
        token = request.COOKIES.get('jwt')
        if not token:
            raise AuthenticationFailed('Unauthenticated!')

        try:
            payload = jwt.decode(token, 'secret', algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Unauthenticated!')
        except jwt.DecodeError:
            raise AuthenticationFailed('Invalid token!')

        # Obtener todas las categorías
        categorias = ConfigCategoria.objects.all()

        # Filtro de búsqueda (opcional)
        search_query = request.GET.get('search')
        if search_query:
            categorias = categorias.filter(nombre__icontains=search_query)

        # Configurar paginación
        paginator = PageNumberPagination()
        paginated_categorias = paginator.paginate_queryset(categorias, request)

        # Serializar los resultados paginados
        serializer = ConfigCategoriaSerializer(paginated_categorias, many=True)

        return paginator.get_paginated_response(serializer.data)

class DeleteCategoriaView(APIView):
    def delete(self, request, encrypted_id):
        # Autenticación
        token = request.COOKIES.get('jwt')
        if not token:
            raise AuthenticationFailed('Unauthenticated!')

        try:
            payload = jwt.decode(token, 'secret', algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Unauthenticated!')
        except jwt.DecodeError:
            raise AuthenticationFailed('Invalid token!')

        # Decodificar el `encrypted_id` para obtener el ID real
        try:
            categoria_id = base64.urlsafe_b64decode(encrypted_id).decode()
        except Exception:
            return Response({'error': 'Invalid encrypted ID.'}, status=status.HTTP_400_BAD_REQUEST)

        # Buscar la categoría por ID
        try:
            categoria = ConfigCategoria.objects.get(id=categoria_id)
        except ConfigCategoria.DoesNotExist:
            return Response({'error': 'Category not found.'}, status=status.HTTP_404_NOT_FOUND)

        # Actualizar los campos de eliminación lógica
        categoria.deleted_user = User.objects.get(id=payload['id'])
        categoria.deleted_at = timezone.now()

        # Guardar los cambios
        categoria.save()

        return Response({'message': 'Category marked as deleted successfully.'}, status=status.HTTP_200_OK)


################MARCAS###########################